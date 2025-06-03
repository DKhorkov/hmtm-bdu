from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.logging.config import logger, shutdown_loggers
from src.logging.enums import Levels


@asynccontextmanager
async def lifespan(app: FastAPI):
    await logger(level=Levels.INFO, message="SERVICE WAS STARTED")
    # When starting
    yield
    # When stopping
    await logger(level=Levels.WARNING, message="SERVICE HAS BEEN STOPPED!")
    await shutdown_loggers()
