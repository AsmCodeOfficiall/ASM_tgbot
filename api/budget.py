from dataclasses import dataclass


@dataclass
class BudgetSplit:
    fund_amount: float
    dev_amount: float
    dev_ids: list[int]


def calculate_split(amount: float, raw_dev_ids: list[int]) -> BudgetSplit:
    dev_ids = [d for d in raw_dev_ids if d != 0]
    dev_count = len(dev_ids)

    fund_amount = round(amount * 0.10, 2)

    if dev_count > 0:
        total_dev_share = amount * 0.30 * 3
        dev_amount = round(total_dev_share / dev_count, 2)
    else:
        dev_amount = 0.0

    return BudgetSplit(
        fund_amount=fund_amount,
        dev_amount=dev_amount,
        dev_ids=dev_ids,
    )
