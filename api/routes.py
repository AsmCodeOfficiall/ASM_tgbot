import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.auth import get_current_user
from api.budget import calculate_split
from api.db import Project, Team, TeamMember, Transaction, User, get_session

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    amount: float = Field(gt=0)
    description: str | None = None


class TeamCreate(BaseModel):
    name: str = Field(min_length=1)
    tax: float = Field(default=10.0, ge=0, le=100)


class TeamJoin(BaseModel):
    invite_code: str = Field(min_length=1)
    payout_percent: float | None = Field(default=None, ge=0, le=100)


class TeamMemberPercentUpdate(BaseModel):
    payout_percent: float = Field(ge=0, le=100)


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)


class WithdrawalCreate(BaseModel):
    amount: float = Field(gt=0)


async def get_or_create_user(session: AsyncSession, user_data: dict) -> User:
    telegram_id = int(user_data.get("id"))
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
        )
        session.add(user)
        await session.flush()
        return user

    user.username = user_data.get("username")
    user.first_name = user_data.get("first_name")
    return user


async def get_user_team_member(session: AsyncSession, user: User) -> TeamMember | None:
    result = await session.execute(
        select(TeamMember)
        .options(selectinload(TeamMember.team))
        .where(TeamMember.user_id == user.id)
    )
    return result.scalar_one_or_none()


async def get_team_members(session: AsyncSession, team_id: int) -> list[TeamMember]:
    result = await session.execute(
        select(TeamMember)
        .options(selectinload(TeamMember.user))
        .where(TeamMember.team_id == team_id)
        .order_by(TeamMember.id)
    )
    return result.scalars().all()


async def get_team_fund(session: AsyncSession, team_id: int) -> float:
    result = await session.execute(
        select(func.coalesce(func.sum(Transaction.value), 0.0))
        .where(
            Transaction.team_id == team_id,
            Transaction.type.in_(["fund", "expense"]),
        )
    )
    return float(result.scalar_one() or 0.0)


async def get_team_by_invite_code(session: AsyncSession, invite_code: str) -> Team | None:
    result = await session.execute(select(Team).where(Team.invite_code == invite_code))
    return result.scalar_one_or_none()


def serialize_member(member: TeamMember) -> dict:
    return {
        "id": member.id,
        "team_id": member.team_id,
        "user_id": member.user_id,
        "role": member.role,
        "payout_percent": member.payout_percent,
        "username": member.user.username,
        "first_name": member.user.first_name,
        "name": member.user.first_name or member.user.username or "Розробник",
        "balance": member.user.balance,
    }


@router.get("/api/dashboard")
async def get_dashboard(
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_data)
    team_member = await get_user_team_member(session, user)

    current_team = team_member.team if team_member else None
    team_id = current_team.id if current_team else None

    members = []
    fund = 0.0

    if current_team:
        members = [serialize_member(member) for member in await get_team_members(session, current_team.id)]
        fund = await get_team_fund(session, current_team.id)

    # Last 10 transactions for this user, with project name eagerly loaded
    tx_result = await session.execute(
        select(Transaction)
        .options(selectinload(Transaction.project))
        .where(Transaction.team_id == team_id)
        .order_by(Transaction.created_at.desc())
        .limit(20)
    )
    transactions = tx_result.scalars().all()

    tx_list = [
        {
            "id": tx.id,
            "type": tx.type,
            "value": tx.value,
            "created_at": tx.created_at.isoformat(),
            # project_name was missing before — now included
            "project_name": tx.project.name if tx.project else None,
        }
        for tx in transactions
    ]

    # Load projects for the team
    projects_list = []
    if current_team:
        proj_result = await session.execute(
            select(Project).where(Project.team_id == current_team.id).order_by(Project.created_at.desc())
        )
        projects = proj_result.scalars().all()
        projects_list = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "amount": p.amount,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
            }
            for p in projects
        ]

    return {
        "fund": fund,
        "balance": user.balance,
        "has_team": bool(current_team),
        "role": team_member.role if team_member else "member",
        "tax": current_team.tax_percent if current_team else 10,
        "team": {
            "id": current_team.id,
            "name": current_team.name,
            "invite_code": current_team.invite_code,
        }
        if current_team
        else None,
        "members": members,
        "projects": projects_list,
        "transactions": tx_list,
    }


@router.post("/api/teams")
async def create_team(
    team_data: TeamCreate,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_data)

    existing_member = await get_user_team_member(session, user)
    if existing_member:
        raise HTTPException(status_code=400, detail="user already belongs to a team")

    for _ in range(5):
        invite_code = secrets.token_urlsafe(8)
        existing_team = await get_team_by_invite_code(session, invite_code)
        if existing_team is None:
            team = Team(
                name=team_data.name,
                owner_user_id=user.id,
                invite_code=invite_code,
                tax_percent=team_data.tax,
            )
            session.add(team)
            await session.flush()

            member = TeamMember(
                team_id=team.id,
                user_id=user.id,
                role="leader",
                payout_percent=100.0,
            )
            session.add(member)
            await session.commit()
            return {
                "status": "success",
                "team": {
                    "id": team.id,
                    "name": team.name,
                    "invite_code": team.invite_code,
                },
                "member": serialize_member(member),
            }

    raise HTTPException(status_code=500, detail="failed to generate invite code")


async def join_team_by_invite_code(
    session: AsyncSession,
    user_data: dict,
    invite_code: str,
    payout_percent: float | None = 0.0,
) -> tuple[Team, TeamMember]:
    user = await get_or_create_user(session, user_data)
    team = await get_team_by_invite_code(session, invite_code)
    
    if team is None:
        raise ValueError("Team not found")

    existing_member = await get_user_team_member(session, user)
    if existing_member and existing_member.team_id != team.id:
        raise ValueError("User already belongs to another team")

    if existing_member is None:
        member = TeamMember(
            team_id=team.id,
            user_id=user.id,
            role="member",
            payout_percent=payout_percent or 0.0,
        )
        session.add(member)
        await session.flush()
        member_to_return = member
    else:
        # We do not update the payout_percent for existing members here.
        # This prevents the bot (which passes 0.0 by default) from resetting their percent,
        # and also prevents users from bypassing the leader's permission to change percents.
        member_to_return = existing_member

    await session.commit()
    return team, member_to_return


@router.post("/api/teams/join")
async def join_team(
    join_data: TeamJoin,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        team, member = await join_team_by_invite_code(
            session=session,
            user_data=user_data,
            invite_code=join_data.invite_code,
            payout_percent=join_data.payout_percent
        )
    except ValueError as exc:
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    return {
        "status": "success",
        "team": {
            "id": team.id,
            "name": team.name,
            "invite_code": team.invite_code,
        },
        "member": serialize_member(member),
    }


@router.patch("/api/teams/members/{member_id}/percent")
async def update_member_percent(
    member_id: int,
    payload: TeamMemberPercentUpdate,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_data)
    current_member = await get_user_team_member(session, user)

    if current_member is None or current_member.role != "leader":
        raise HTTPException(status_code=403, detail="only team leaders can update payouts")

    result = await session.execute(select(TeamMember).where(TeamMember.id == member_id))
    target_member = result.scalar_one_or_none()

    if target_member is None or target_member.team_id != current_member.team_id:
        raise HTTPException(status_code=404, detail="member not found")

    target_member.payout_percent = payload.payout_percent
    await session.commit()
    await session.refresh(target_member)

    return {"status": "success", "member": serialize_member(target_member)}


@router.post("/api/projects")
async def create_project(
    project_data: ProjectCreate,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_data)
    current_member = await get_user_team_member(session, user)

    if current_member is None:
        raise HTTPException(status_code=400, detail="user is not in a team")

    team = current_member.team
    members = await get_team_members(session, team.id)

    if not members:
        raise HTTPException(status_code=400, detail="team has no members")

    percentages = {member.user_id: member.payout_percent for member in members}
    split = calculate_split(project_data.amount, percentages, team_fund_percent=team.tax_percent)

    project = Project(
        name=project_data.name,
        description=project_data.description,
        amount=project_data.amount,
        team_id=team.id,
    )
    session.add(project)
    await session.flush()

    fund_tx = Transaction(
        user_id=user.id,
        project_id=project.id,
        team_id=team.id,
        type="fund",
        value=split.fund_amount,
    )
    session.add(fund_tx)

    for member in members:
        credit_amount = split.member_amounts.get(member.user_id, 0.0)
        if credit_amount <= 0:
            continue

        member.user.balance += credit_amount
        session.add(
            Transaction(
                user_id=member.user_id,
                project_id=project.id,
                team_id=team.id,
                type="credit",
                value=credit_amount,
            )
        )

    await session.commit()

    return {
        "status": "success",
        "project_id": project.id,
        "team_id": team.id,
        "split": {
            "fund": split.fund_amount,
            "member_amounts": split.member_amounts,
        },
    }


@router.post("/api/teams/expenses")
async def create_expense(
    expense_data: ExpenseCreate,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_data)
    current_member = await get_user_team_member(session, user)

    if current_member is None:
        raise HTTPException(status_code=400, detail="user is not in a team")

    team = current_member.team
    current_fund = await get_team_fund(session, team.id)

    if current_fund < expense_data.amount:
        raise HTTPException(status_code=400, detail="insufficient team fund")

    expense = Transaction(
        user_id=user.id,
        team_id=team.id,
        type="expense",
        value=-expense_data.amount,
    )
    session.add(expense)
    await session.commit()

    return {
        "status": "success",
        "team_fund": round(current_fund - expense_data.amount, 2),
    }


@router.post("/api/withdrawals")
async def create_withdrawal(
    withdrawal_data: WithdrawalCreate,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_data)
    current_member = await get_user_team_member(session, user)

    if current_member is None:
        raise HTTPException(status_code=400, detail="user is not in a team")

    if user.balance < withdrawal_data.amount:
        raise HTTPException(status_code=400, detail="insufficient balance")

    user.balance -= withdrawal_data.amount
    withdrawal = Transaction(
        user_id=user.id,
        team_id=current_member.team_id,
        type="withdrawal",
        value=-withdrawal_data.amount,
    )
    session.add(withdrawal)
    await session.commit()

    return {
        "status": "success",
        "balance": round(user.balance, 2),
    }


# --- Bulk team settings update (Settingsboard) ---

class MemberUpdate(BaseModel):
    id: int
    personal_tax: float = Field(ge=0, le=100)


class TeamSettingsUpdate(BaseModel):
    tax: float = Field(ge=0, le=100)
    members: List[MemberUpdate] = []


@router.put("/api/teams/members")
async def bulk_update_team_settings(
    payload: TeamSettingsUpdate,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    user = await get_or_create_user(session, user_data)
    current_member = await get_user_team_member(session, user)

    if current_member is None or current_member.role != "leader":
        raise HTTPException(status_code=403, detail="only team leaders can update settings")

    team = current_member.team
    team.tax_percent = payload.tax

    # Update each member's payout_percent
    for member_update in payload.members:
        result = await session.execute(
            select(TeamMember).where(TeamMember.id == member_update.id)
        )
        target_member = result.scalar_one_or_none()

        if target_member is None or target_member.team_id != team.id:
            continue  # skip members that don't belong to this team

        target_member.payout_percent = member_update.personal_tax

    await session.commit()

    # Return updated members list
    updated_members = await get_team_members(session, team.id)
    return {
        "status": "success",
        "tax": team.tax_percent,
        "members": [serialize_member(m) for m in updated_members],
    }

