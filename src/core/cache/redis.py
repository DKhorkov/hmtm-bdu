from typing import Any, Optional
from pickle import loads as pickle_loads, dumps as pickle_dumps
from dotenv import load_dotenv, find_dotenv

from redis.asyncio import (
    Redis as AsyncRedis,
    ConnectionPool as AsyncRedisConnectionPool
)
from fastapi import Request

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
        async with self._redis as redis_pool:  # ping может использовать pool
            await redis_pool.ping()

    async def get(self, key: str, request: Request) -> Optional[Any]:  # noqa
        async with self._redis as redis_pool:
            result: Optional[Any] = await redis_pool.get(key)
            return pickle_loads(result) if result else None

    async def set(self, key: str, data: Any, ttl: int, request: Request) -> None:  # noqa
        """Универсальная функция установки любых данных или набора данных (Удобно для кеширования схем)"""
        async with self._redis as redis_pool:
            await redis_pool.set(name=key, value=pickle_dumps(data), ex=ttl)

    async def delete(self, key: str, request: Request) -> None:  # noqa
        async with self._redis as redis_pool:
            await redis_pool.delete(key)

    async def close(self) -> None:
        await self._redis.aclose(close_connection_pool=True)
