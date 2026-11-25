from datetime import date
from decimal import Decimal

import pytest

from bnpl.purchases import Instalment, due_dates, record_purchase, split_amount


def test_split_even_amount():
    assert split_amount(Decimal("90.00"), 3) == [Decimal("30.00")] * 3


def test_split_puts_leftover_cents_first():
    assert split_amount(Decimal("100.00"), 3) == [
        Decimal("33.34"),
        Decimal("33.33"),
        Decimal("33.33"),
    ]


def test_split_always_adds_up_to_the_total():
    for total in ["0.01", "0.05", "19.99", "100.00", "1234.57"]:
        for count in range(1, 7):
            parts = split_amount(Decimal(total), count)
            assert sum(parts) == Decimal(total)
            assert all(p == p.quantize(Decimal("0.01")) for p in parts)


@pytest.mark.parametrize(
    ("total", "count"),
    [("0", 3), ("-10.00", 3), ("10.005", 3), ("10.00", 0)],
)
def test_split_rejects_invalid_input(total, count):
    with pytest.raises(ValueError):
        split_amount(Decimal(total), count)


def test_due_dates_every_two_weeks():
    assert due_dates(date(2026, 12, 1), 4, 14) == [
        date(2026, 12, 1),
        date(2026, 12, 15),
        date(2026, 12, 29),
        date(2027, 1, 12),
    ]


def test_due_dates_reject_zero_interval():
    with pytest.raises(ValueError):
        due_dates(date(2026, 12, 1), 3, 0)


def test_record_purchase_first_instalment_on_purchase_day():
    purchase = record_purchase(
        merchant=" Zalando ",
        provider="Klarna",
        total=Decimal("100.00"),
        purchase_date=date(2026, 11, 25),
        count=3,
        interval_days=30,
    )
    assert purchase.merchant == "Zalando"
    assert purchase.instalments == (
        Instalment(1, date(2026, 11, 25), Decimal("33.34")),
        Instalment(2, date(2026, 12, 25), Decimal("33.33")),
        Instalment(3, date(2027, 1, 24), Decimal("33.33")),
    )


def test_record_purchase_with_later_first_due_date():
    purchase = record_purchase(
        merchant="IKEA",
        provider="PayPal Pay in 3",
        total=Decimal("60.00"),
        purchase_date=date(2026, 11, 25),
        count=3,
        interval_days=30,
        first_due=date(2026, 12, 25),
    )
    assert [i.due_date for i in purchase.instalments][0] == date(2026, 12, 25)


def test_record_purchase_rejects_first_due_before_purchase():
    with pytest.raises(ValueError):
        record_purchase(
            "IKEA",
            "Klarna",
            Decimal("60.00"),
            date(2026, 11, 25),
            3,
            30,
            first_due=date(2026, 11, 1),
        )


def test_record_purchase_rejects_empty_merchant():
    with pytest.raises(ValueError):
        record_purchase("  ", "Klarna", Decimal("60.00"), date(2026, 11, 25), 3, 30)
