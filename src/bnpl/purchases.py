"""Record purchases and split them into instalments.

Owner: Teun Schulten.

A BNPL purchase is paid in a fixed number of instalments, the first one on a
given date and the next ones a fixed number of days apart. This module turns a
purchase into its instalments: the amount of each one, in whole cents, and its
due date. The number of instalments and the days between them come from the
provider's rules (`providers`); storing purchases in the database belongs to
the shared data model (`models`, `db`).
"""

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

CENT = Decimal("0.01")


@dataclass(frozen=True)
class Instalment:
    """One payment of a purchase. `number` starts at 1."""

    number: int
    due_date: date
    amount: Decimal


@dataclass(frozen=True)
class Purchase:
    """A purchase paid with a BNPL provider, and its instalments."""

    merchant: str
    provider: str
    total: Decimal
    purchase_date: date
    instalments: tuple[Instalment, ...]


def split_amount(total: Decimal, count: int) -> list[Decimal]:
    """Splits `total` into `count` amounts in whole cents that add up to `total`.

    The amounts are as equal as possible. The cents that don't divide evenly go
    to the first instalments, one cent each: 100.00 in 3 is 33.34, 33.33, 33.33.
    """
    if count < 1:
        raise ValueError(f"there must be at least 1 instalment, not {count}")
    if total <= 0:
        raise ValueError(f"the total must be positive, not {total}")
    if total != total.quantize(CENT):
        raise ValueError(f"{total} has fractions of a cent")
    cents = int(total * 100)
    base, rest = divmod(cents, count)
    return [Decimal(base + (1 if i < rest else 0)).scaleb(-2) for i in range(count)]


def due_dates(first_due: date, count: int, interval_days: int) -> list[date]:
    """The due dates of `count` instalments, `interval_days` apart."""
    if count < 1:
        raise ValueError(f"there must be at least 1 instalment, not {count}")
    if interval_days < 1:
        raise ValueError(
            f"the days between instalments must be at least 1, not {interval_days}"
        )
    return [first_due + timedelta(days=interval_days * i) for i in range(count)]


def record_purchase(
    merchant: str,
    provider: str,
    total: Decimal,
    purchase_date: date,
    count: int,
    interval_days: int,
    first_due: date | None = None,
) -> Purchase:
    """A purchase with its instalments.

    The first instalment is due on `first_due`, or on the day of the purchase if
    it is not given (Klarna and Afterpay charge the first one at checkout).
    """
    if not merchant.strip():
        raise ValueError("the merchant can't be empty")
    if not provider.strip():
        raise ValueError("the provider can't be empty")
    first = purchase_date if first_due is None else first_due
    if first < purchase_date:
        raise ValueError(
            f"the first instalment ({first}) is before the purchase ({purchase_date})"
        )
    amounts = split_amount(total, count)
    dates = due_dates(first, count, interval_days)
    instalments = tuple(
        Instalment(number=i, due_date=d, amount=a)
        for i, (d, a) in enumerate(zip(dates, amounts, strict=True), start=1)
    )
    return Purchase(
        merchant=merchant.strip(),
        provider=provider.strip(),
        total=total,
        purchase_date=purchase_date,
        instalments=instalments,
    )
