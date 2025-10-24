from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logger.enums import Levels
from src.core.root.config import config
from src.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bff_gql_client = config.bff_gql_client  # noqa
    app.state.redis = config.redis_as_cache  # noqa

    try:
        await config.redis_as_cache.ping()
        await logger.write(level=Levels.INFO, message="SERVICE WAS LAUNCHED CORRECTLY")

        yield

        await logger.write(level=Levels.INFO, message="SERVICE HAS BEEN STOPPED!")

    except Exception as error:
        await logger.write(level=Levels.ERROR, message=str(error))
        raise

    finally:
        await logger.shutdown()
        await config.redis_as_cache.close()
