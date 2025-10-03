from functools import wraps
from typing import Callable, Any, Optional, TYPE_CHECKING

from redis import RedisError
from fastapi import Request

from src.core.cache.schemas import RedisErrorValidationModel
from src.core.logger.enums import Levels
from src.core.logger.logger import Logger
from src.core.cache.constants import EXCLUDE_CACHE_KWARGS

if TYPE_CHECKING:
    from src.core.cache.redis import Redis


class RedisWrappers:

    @staticmethod
    def redis_cache(ttl: int) -> Callable:
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                """
                    Декоратор с "абсолютной" вариативностью входных данных. Использовать с осторожностью.
                    Рекомендуется настроить "вытесняемый" кеш, либо поменять настройки ключа
                """
                key: str = (
                    f"{func.__name__}:"
                    f"{':'.join(str(value) for key, value in kwargs.items() if key not in EXCLUDE_CACHE_KWARGS)}"
                )  # Чистый ключ без доп. лишних параметров

                request: Optional[Request] = kwargs.get("request")

                redis: Redis = request.app.state.redis  # type: ignore
                logger: Logger = request.app.state.logger  # type: ignore

                try:

                    await redis.ping()
                    redis_response: Optional[Any] = await redis.get(key=key, request=request)  # type: ignore

                    if redis_response is not None:
                        return redis_response

                    func_response: Any = await func(*args, **kwargs)
                    await redis.set(key=key, data=func_response, ttl=ttl, request=request)  # type: ignore
                    return func_response

                except Exception as error:
                    await logger.write_log(level=Levels.ERROR, message=str(error))
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def redis_error_handler(cls):
        """Декоратор для глобальной обработки ошибок на уровне класса (Поддерживает ТОЛЬКО асинхронные методы)"""

        class WrappedClass(cls):  # type: ignore
            def __getattribute__(self, name: str):
                func = super().__getattribute__(name)

                if name in ["ping", "close"]:
                    return func

                if callable(func) and not name.startswith("__"):
                    @wraps(func)
                    async def wrapper(*args, **kwargs) -> Any:
                        request: Optional[Request] = kwargs.get("request")
                        logger: Logger = request.app.state.logger  # type: ignore

                        try:
                            return await func(*args, **kwargs)

                        except Exception as error:
                            error_validator: RedisErrorValidationModel = RedisErrorValidationModel(error=str(error))

                            await logger.write_log(level=Levels.ERROR, message=error_validator.error)
                            raise RedisError(error_validator.error)

                    return wrapper
                return func

        return WrappedClass
