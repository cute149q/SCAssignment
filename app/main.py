import logging
import os
from contextlib import asynccontextmanager
from enum import Enum

import fastapi
from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse

from app.dependencies.dependencies_resolver import DependenciesResolver
from app.dependencies.settings import get_app_settings
from app.models.settings import AppSettings
from app.routes.timer import timer_router


class Tag(str, Enum):
    TIMER = "timer"
    HEALTHCHECK = "healthcheck"


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=unused-argument
    app_settings: AppSettings = get_app_settings()
    await DependenciesResolver.init_dependencies(app_settings)
    yield
    # Clean up context managers pushed to the exit stack.
    await DependenciesResolver.destroy()


app = fastapi.FastAPI(
    title="Timer API",
    description="A simple API to set and get timers",
    version="0.1.0",
    openapi_tags=[
        {"name": Tag.TIMER.value, "description": "Operations related to timers"},
    ],
    default_response_class=JSONResponse,
    docs_url=("/docs" if "ENABLE_DOCS" in os.environ else None),
    redoc_url=("/redoc" if "ENABLE_DOCS" in os.environ else None),
    openapi_url=("/openapi.json" if "ENABLE_DOCS" in os.environ else None),
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get(
    "/healthcheck",
    tags=[Tag.HEALTHCHECK.value],
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
async def healthcheck():
    logger.info("Healthcheck OK")
    return {"message": "OK"}


app.include_router(timer_router, tags=[Tag.TIMER], prefix="/timer")
