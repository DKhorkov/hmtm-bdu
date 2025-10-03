from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logger.enums import Levels
from src.core.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.gql_client = config.graphql_client  # noqa
    app.state.redis = config.redis_as_cache  # noqa
    app.state.logger = config.logger  # noqa
    app.state.cryptography = config.get_encryptor()  # noqa

    try:
        await config.redis_as_cache.ping()
        await config.logger.init_logger()
        await config.logger.write_log(level=Levels.INFO, message="SERVICE WAS LAUNCHED CORRECTLY")

        yield

        await config.logger.write_log(level=Levels.INFO, message="SERVICE HAS BEEN STOPPED!")

    except Exception as error:
        await config.logger.write_log(level=Levels.ERROR, message=str(error))
        raise

    finally:
        await config.logger.shutdown()
        await config.redis_as_cache.close()
