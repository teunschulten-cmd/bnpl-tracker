"""The FastAPI application. Each module adds its router under /api/<module>/.

This is a minimal shared skeleton so the team runs one application. Including
the routers here overlaps with Máximo Beras-Goico's shared job (the interface
that ties the modules together). Each member still owns the router of their
own module.
"""

import importlib
from contextlib import asynccontextmanager

from fastapi import FastAPI

from bnpl.db import create_tables

# Each module adds its router module here as it lands, for example
# "bnpl.purchases.router". The module must expose `router`.
MODULE_ROUTERS = ("bnpl.purchases.router",)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_tables()
    yield


def include_module_routers(app: FastAPI) -> None:
    for name in MODULE_ROUTERS:
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        app.include_router(module.router)


def create_app() -> FastAPI:
    app = FastAPI(
        title="BNPL tracker",
        description="Track Buy Now, Pay Later purchases, instalments and debt.",
        lifespan=lifespan,
    )
    include_module_routers(app)
    return app


app = create_app()
