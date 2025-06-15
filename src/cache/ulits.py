from typing import NoReturn

from redis.exceptions import (
    ConnectionError as RedisConnectionError,
    AuthenticationError as RedisAuthenticationError
)
from src.logging.config import logger
from src.logging.enums import Levels
from src.cache.constants import REDIS_ERRORS, DEFAULT_REDIS_ERROR_MESSAGE


async def redis_error_handler(error: Exception) -> NoReturn:
    error_message: str = (
        REDIS_ERRORS.get("Error 111")  # type: ignore[assignment]
        if str(error).startswith("Error 111")
        else REDIS_ERRORS.get(str(error), DEFAULT_REDIS_ERROR_MESSAGE)
    )

    if isinstance(error, RedisConnectionError):
        await logger(level=Levels.ERROR, message=error_message)
        raise RedisConnectionError(error_message)

    elif isinstance(error, RedisAuthenticationError):
        await logger(level=Levels.ERROR, message=error_message)
        raise RedisAuthenticationError(error_message)

    else:
        await logger(level=Levels.ERROR, message=error_message)
        raise Exception(error_message)
