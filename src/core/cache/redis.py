from typing import Any, Optional, Literal
from pickle import loads as pickle_loads, dumps as pickle_dumps
from dotenv import load_dotenv, find_dotenv

from redis.asyncio import (
    Redis as AsyncRedis,
    ConnectionPool as AsyncRedisConnectionPool
)

from src.core.cache.schemas import RedisConfig
from src.core.cache.wrappers import RedisWrappers

load_dotenv(find_dotenv(".env"))


@RedisWrappers.redis_error_handler
class Redis:
    def __init__(self, redis: RedisConfig) -> None:
        self._redis: AsyncRedis = AsyncRedis(
            connection_pool=AsyncRedisConnectionPool(**redis.model_dump())
        )

    async def ping(self) -> None:
        await self._redis.ping()

    async def get(self, key: str) -> Optional[Any]:
        result: Optional[Any] = await self._redis.get(key)
        return pickle_loads(result) if result else None

    async def set(self, key: str, data: Any, ttl: int) -> Optional[Literal[True]]:
        """Универсальная функция установки любых данных или набора данных (Удобно для кеширования схем)"""
        await self._redis.set(name=key, value=pickle_dumps(data), ex=ttl)
        return True  # Для аудита

    async def delete(self, key: str) -> Optional[Literal[True]]:
        await self._redis.delete(key)
        return True

    async def close(self) -> Optional[Literal[True]]:
        await self._redis.aclose(close_connection_pool=True)
        return True
