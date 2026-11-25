"""Record purchases and split them into instalments.

Owner: Teun Schulten.
"""

from bnpl.purchases.service import (
    Instalment,
    Purchase,
    due_dates,
    record_purchase,
    split_amount,
)

__all__ = [
    "Instalment",
    "Purchase",
    "due_dates",
    "record_purchase",
    "split_amount",
]
