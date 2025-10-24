from functools import wraps
from typing import Callable, Any, Optional, TYPE_CHECKING

from redis import RedisError

from src.core.cache.schemas import RedisErrorValidation
from src.core.logger.enums import Levels
from src.core.cache.constants import EXCLUDE_CACHE_KWARGS
from src.core.logger import logger

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
                )  # Чистый ключ без доп-ых лишних параметров

                redis: Optional[Redis] = kwargs.get("redis")
                assert redis is not None

                try:

                    await redis.ping()
                    response: Optional[Any] = await redis.get(key=key)

                    if response is not None:
                        return response

                    func_response: Any = await func(*args, **kwargs)
                    await redis.set(key=key, data=func_response, ttl=ttl)
                    return func_response

                except Exception as error:
                    await logger.write(level=Levels.ERROR, message=f"Redis cache error | Detail: {error}")
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def redis_error_handler(cls):
        """Декоратор для глобальной обработки ошибок на уровне класса (Поддерживает ТОЛЬКО асинхронные методы)"""

        class WrappedClass(cls):  # type: ignore
            def __getattribute__(self, name: str):
                func = super().__getattribute__(name)

                if name == "close":
                    return func

                if callable(func) and not name.startswith("__"):
                    @wraps(func)
                    async def wrapper(*args, **kwargs) -> Any:
                        try:
                            return await func(*args, **kwargs)

                        except Exception as error:
                            error_validator: RedisErrorValidation = RedisErrorValidation(
                                orig_error=str(error))

                            await logger.write(level=Levels.ERROR, message=error_validator.message())
                            raise RedisError(error_validator.message())

                    return wrapper
                return func

        return WrappedClass
