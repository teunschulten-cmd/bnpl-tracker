"""The database: the connection, the session and the declarative base.

This is a minimal shared skeleton so every module can declare its own table
and read and write through a session. The full data model and schema belong
to Justin Van Vuren (shared job: models and database).
"""

import importlib
import os
from decimal import Decimal

from sqlalchemy import Integer, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.types import TypeDecorator

# Override with PostgreSQL later, for example:
# DATABASE_URL=postgresql+psycopg://user:pass@host/dbname
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///bnpl.db")


class Money(TypeDecorator):
    """An amount: a Decimal in Python, a whole number of cents in the database.

    SQLite has no exact decimal type, so amounts are stored as an integer number
    of cents (100.00 → 10000). When the team moves to PostgreSQL, the same
    amounts can be stored as NUMERIC. The rest of the program only sees Decimal.
    Never use float for money.
    """

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        cents = value * 100
        if cents != cents.to_integral_value():
            raise ValueError(f"{value} has fractions of a cent")
        return int(cents)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Decimal(value).scaleb(-2)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    """SQLite checks foreign keys only when asked to, once per connection."""
    if engine.dialect.name == "sqlite":
        dbapi_connection.execute("PRAGMA foreign_keys = ON")


# Each module adds its table module here as it lands, for example
# "bnpl.purchases.tables". create_tables imports them so Base.metadata
# includes every table before it is created.
MODULE_TABLES = ("bnpl.purchases.tables",)


def import_module_tables() -> None:
    """Import each module's tables so they are registered on Base."""
    for name in MODULE_TABLES:
        try:
            importlib.import_module(name)
        except ModuleNotFoundError:
            continue


def create_tables() -> None:
    """Creates the tables that don't exist yet. Existing tables are not changed."""
    import_module_tables()
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
