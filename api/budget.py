from dataclasses import dataclass


@dataclass
class BudgetSplit:
    fund_amount: float
    member_amounts: dict[int, float]


def calculate_split(amount: float, member_percentages: dict[int, float], team_fund_percent: float = 10.0) -> BudgetSplit:
    fund_share = team_fund_percent / 100.0
    fund_amount = round(amount * fund_share, 2)
    dev_pool = round(amount - fund_amount, 2)

    if not member_percentages:
        return BudgetSplit(fund_amount=round(fund_amount + dev_pool, 2), member_amounts={})

    total_percent = sum(max(0.0, pct) for pct in member_percentages.values())
    if total_percent <= 0:
        return BudgetSplit(fund_amount=round(fund_amount + dev_pool, 2), member_amounts={})

    member_amounts = {}
    total_allocated = 0.0

    for member_id, pct in member_percentages.items():
        ratio = max(0.0, pct) / total_percent
        member_amount = round(dev_pool * ratio, 2)
        member_amounts[member_id] = member_amount
        total_allocated += member_amount

    remainder = round(dev_pool - total_allocated, 2)
    fund_amount = round(fund_amount + remainder, 2)

    return BudgetSplit(fund_amount=fund_amount, member_amounts=member_amounts)
