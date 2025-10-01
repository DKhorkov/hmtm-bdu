from functools import wraps
from typing import Callable, Any, Optional, TYPE_CHECKING

from redis import RedisError

from src.core.cache.schemas import RedisErrorValidationModel
from src.core.logger.enums import Levels

if TYPE_CHECKING:
    from src.core.cache.redis import Redis


class RedisWrappers:

    @staticmethod
    def redis_cache(ttl: int, redis: "Redis") -> Callable:
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                """
                    Декоратор с "абсолютной" вариативностью входных данных. Использовать с осторожностью.
                    Рекомендуется настроить "вытесняемый" кеш, либо поменять настройки ключа
                """
                key: str = f"{func.__name__}:{':'.join(str(value) for value in kwargs.values())}"
                try:
                    await redis.ping()
                    redis_response: Optional[Any] = await redis.get(key=key)

                    if redis_response is not None:
                        return redis_response

                    func_response: Any = await func(*args, **kwargs)
                    await redis.set(key=key, data=func_response, ttl=ttl)
                    return func_response

                except Exception as error:
                    from src.core.config import config  # Lazy init

                    await config.logger.write_log(level=Levels.ERROR, message=str(error))
                    return await func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def redis_error_handler(cls):
        """Декоратор для глобальной обработки ошибок на уровне класса (Поддерживает ТОЛЬКО асинхронные методы)"""

        class WrappedClass(cls):  # type: ignore
            def __getattribute__(self, name: str):
                func = super().__getattribute__(name)

                if callable(func) and not name.startswith("__"):
                    @wraps(func)
                    async def wrapper(*args, **kwargs) -> Any:
                        try:
                            return await func(*args, **kwargs)

                        except Exception as error:
                            from src.core.config import config  # Lazy init

                            error_validator: RedisErrorValidationModel = RedisErrorValidationModel(error=str(error))

                            await config.logger.write_log(level=Levels.ERROR, message=error_validator.error)
                            raise RedisError(error_validator.error)

                    return wrapper
                return func

        return WrappedClass
