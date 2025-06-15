from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.logging.config import logger, shutdown_loggers
from src.logging.enums import Levels
from src.cache.config import RedisConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await RedisConfig().connect()
        await logger(level=Levels.INFO, message="SERVICE WAS LAUNCHED CORRECTLY")
        # When starting
        yield
        # When stopping
        await logger(level=Levels.INFO, message="SERVICE HAS BEEN STOPPED!")

    except Exception as error:
        await logger(level=Levels.ERROR, message=str(error))
        raise

    finally:
        await shutdown_loggers()
        await RedisConfig().close()
