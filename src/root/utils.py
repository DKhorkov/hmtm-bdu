from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.common.logger_config import shutdown_loggers, logger
from src.common.enums import Levels


@asynccontextmanager
async def lifespan(app: FastAPI):
    await logger(level=Levels.INFO, message="SERVICE WAS STARTED")
    yield
    await logger(level=Levels.WARNING, message="SERVICE HAS BEEN STOPPED!")
    await shutdown_loggers()
