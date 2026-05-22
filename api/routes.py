from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from api.db import get_session, User, Project, Transaction
from api.auth import get_current_user
from api.config import settings
from api.budget import calculate_split

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    amount: float


@router.get("/api/dashboard")
async def get_dashboard(
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    telegram_id = user_data.get("id")

    user_result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    balance = user.balance

    # Sum all fund transactions across the whole team
    fund_result = await session.execute(
        select(func.sum(Transaction.value)).where(Transaction.type == "fund")
    )
    fund = fund_result.scalar_one_or_none() or 0.0

    # Last 10 transactions for this user, with project name eagerly loaded
    tx_result = await session.execute(
        select(Transaction)
        .options(selectinload(Transaction.project))
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(10)
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

    return {"fund": fund, "balance": balance, "transactions": tx_list}


@router.post("/api/projects")
async def create_project(
    project_data: ProjectCreate,
    user_data: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    telegram_id = user_data.get("id")

    creator_res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    creator = creator_res.scalar_one_or_none()
    if not creator:
        creator = User(
            telegram_id=telegram_id,
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
        )
        session.add(creator)
        await session.flush()

    project = Project(name=project_data.name, amount=project_data.amount)
    session.add(project)
    await session.flush()

    # Delegate all math to budget module
    split = calculate_split(
        amount=project_data.amount,
        raw_dev_ids=[
            settings.DEV_TELEGRAM_ID_1,
            settings.DEV_TELEGRAM_ID_2,
            settings.DEV_TELEGRAM_ID_3,
        ],
    )

    # Fund transaction (includes unallocated shares from missing devs)
    fund_tx = Transaction(
        user_id=creator.id,
        project_id=project.id,
        type="fund",
        value=split.fund_amount,
    )
    session.add(fund_tx)

    # Developer income transactions
    # type="credit" matches the frontend TYPE_LABELS and color logic
    for d_id in split.dev_ids:
        res = await session.execute(select(User).where(User.telegram_id == d_id))
        u = res.scalar_one_or_none()
        if not u:
            u = User(telegram_id=d_id)
            session.add(u)
            await session.flush()

        u.balance += split.dev_amount
        tx = Transaction(
            user_id=u.id,
            project_id=project.id,
            type="credit",          # ← was "income", caused frontend mismatch
            value=split.dev_amount,
        )
        session.add(tx)

    await session.commit()
    return {
        "status": "success",
        "project_id": project.id,
        "split": {
            "fund": split.fund_amount,
            "per_dev": split.dev_amount,
            "dev_count": len(split.dev_ids),
        },
    }
