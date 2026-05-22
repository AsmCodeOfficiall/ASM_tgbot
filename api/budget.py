"""
Budget distribution logic.

Distribution rule (per ТЗ):
  10%  → team fund
  30%  → each developer (up to 3)
  ---
  If fewer than 3 devs are configured (IDs == 0), the unassigned
  30% shares are added back to the fund so no money is lost.
"""
from dataclasses import dataclass, field
from typing import List

FUND_SHARE = 0.10
DEV_SHARE = 0.30
MAX_DEVS = 3


@dataclass
class BudgetSplit:
    fund_amount: float          # total amount going to the team fund
    dev_amount: float           # amount per developer
    dev_ids: List[int]          # filtered list of active developer telegram IDs
    remainder: float            # unallocated remainder (added to fund)


def calculate_split(amount: float, raw_dev_ids: List[int]) -> BudgetSplit:
    """
    Calculate budget distribution for a given project amount.

    Args:
        amount:      Total project amount in USD.
        raw_dev_ids: List of developer Telegram IDs (0 means "not set").

    Returns:
        BudgetSplit with all amounts rounded to 2 decimal places.
    """
    active_devs = [d for d in raw_dev_ids if d and d != 0]

    fund_base = round(amount * FUND_SHARE, 2)
    dev_amount = round(amount * DEV_SHARE, 2)

    # Money for devs that don't exist goes back to fund
    missing_devs = MAX_DEVS - len(active_devs)
    remainder = round(dev_amount * missing_devs, 2)

    # Correct for floating-point drift on the last cent
    total_check = fund_base + dev_amount * len(active_devs) + remainder
    drift = round(amount - total_check, 2)
    fund_total = round(fund_base + remainder + drift, 2)

    return BudgetSplit(
        fund_amount=fund_total,
        dev_amount=dev_amount,
        dev_ids=active_devs,
        remainder=remainder,
    )
