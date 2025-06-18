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

    await logger(level=Levels.ERROR, message=error_message)
    if isinstance(error, RedisConnectionError):
        raise RedisConnectionError(error_message)

    elif isinstance(error, RedisAuthenticationError):
        raise RedisAuthenticationError(error_message)

    else:
        raise Exception(error_message)
