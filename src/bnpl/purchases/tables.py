"""The purchases table.

Owner: Teun Schulten.

A purchase is the module's main entity. The instalments of a purchase are
computed from the stored total, count, interval and first due date, so this
table is enough for the create and list endpoints. Marking instalments paid
belongs to the schedule module.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from bnpl.db import Base, Money


class PurchaseRow(Base):
    """One row of the table `purchases`."""

    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant: Mapped[str] = mapped_column(String(200))
    provider: Mapped[str] = mapped_column(String(100))
    total: Mapped[Decimal] = mapped_column(Money)
    purchase_date: Mapped[date]
    instalment_count: Mapped[int] = mapped_column(Integer)
    interval_days: Mapped[int] = mapped_column(Integer)
    first_due: Mapped[date]
