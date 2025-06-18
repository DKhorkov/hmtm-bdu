from functools import wraps
from typing import Callable, Any, Optional

from src.redis.config import redis
from src.logging.config import logger
from src.logging.enums import Levels


def redis_cache(ttl: int) -> Callable:
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            key: str = f"{func.__name__}:{':'.join(str(value) for value in kwargs.values())}"

            try:
                await redis.ping()
                redis_response: Optional[Any] = await redis.get(key=key)

                if redis_response is not None:
                    return redis_response

                else:
                    func_response: Any = await func(*args, **kwargs)
                    await redis.set(key=key, data=func_response, ttl=ttl)
                    return func_response

            except Exception as error:
                await logger(level=Levels.ERROR, message=str(error))
                return await func(*args, **kwargs)

        return wrapper

    return decorator
