"""HTTP endpoints for purchases: create and list.

Owner: Teun Schulten.

POST /api/purchases/ records a purchase, splits it into instalments and
writes the purchase to the database. GET /api/purchases/ lists the purchases
already stored. Amounts in the JSON are decimal strings, for example "100.00",
never floats.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_serializer, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from bnpl.db import get_session
from bnpl.purchases.service import Purchase, record_purchase
from bnpl.purchases.tables import PurchaseRow

router = APIRouter(prefix="/api/purchases", tags=["purchases"])


class PurchaseIn(BaseModel):
    """Body of POST /api/purchases/."""

    merchant: str
    provider: str
    total: Decimal
    purchase_date: date
    count: int = Field(ge=1)
    interval_days: int = Field(ge=1)
    first_due: date | None = None

    @field_validator("total", mode="before")
    @classmethod
    def total_must_be_a_decimal_string(cls, value: object) -> Decimal:
        if isinstance(value, float):
            raise ValueError(
                "send the amount as a string, for example '100.00', "
                "not as a JSON number"
            )
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))


class InstalmentOut(BaseModel):
    number: int
    due_date: date
    amount: Decimal

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return f"{value:.2f}"


class PurchaseOut(BaseModel):
    id: int
    merchant: str
    provider: str
    total: Decimal
    purchase_date: date
    count: int
    interval_days: int
    first_due: date
    instalments: list[InstalmentOut]

    @field_serializer("total")
    def serialize_total(self, value: Decimal) -> str:
        return f"{value:.2f}"


def _to_out(row: PurchaseRow, purchase: Purchase) -> PurchaseOut:
    return PurchaseOut(
        id=row.id,
        merchant=row.merchant,
        provider=row.provider,
        total=row.total,
        purchase_date=row.purchase_date,
        count=row.instalment_count,
        interval_days=row.interval_days,
        first_due=row.first_due,
        instalments=[
            InstalmentOut(
                number=item.number, due_date=item.due_date, amount=item.amount
            )
            for item in purchase.instalments
        ],
    )


def _from_row(row: PurchaseRow) -> Purchase:
    return record_purchase(
        merchant=row.merchant,
        provider=row.provider,
        total=row.total,
        purchase_date=row.purchase_date,
        count=row.instalment_count,
        interval_days=row.interval_days,
        first_due=row.first_due,
    )


def session_dep():
    session = get_session()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(session_dep)]


@router.post("/", status_code=201, response_model=PurchaseOut)
def create_purchase(body: PurchaseIn, session: SessionDep) -> PurchaseOut:
    try:
        purchase = record_purchase(
            merchant=body.merchant,
            provider=body.provider,
            total=body.total,
            purchase_date=body.purchase_date,
            count=body.count,
            interval_days=body.interval_days,
            first_due=body.first_due,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    first_due = purchase.instalments[0].due_date
    row = PurchaseRow(
        merchant=purchase.merchant,
        provider=purchase.provider,
        total=purchase.total,
        purchase_date=purchase.purchase_date,
        instalment_count=len(purchase.instalments),
        interval_days=body.interval_days,
        first_due=first_due,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return _to_out(row, purchase)


@router.get("/", response_model=list[PurchaseOut])
def list_purchases(session: SessionDep) -> list[PurchaseOut]:
    rows = session.scalars(select(PurchaseRow).order_by(PurchaseRow.id)).all()
    return [_to_out(row, _from_row(row)) for row in rows]
