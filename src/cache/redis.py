from typing import Any, Optional, Literal
from pickle import loads as pickle_loads, dumps as pickle_dumps
from os import getenv

from redis.asyncio import (
    Redis as AsyncRedis,
    ConnectionPool as AsyncRedisConnectionPool
)
from src.cache.ulits import redis_error_handler
from src.cache.constants import (
    DB,
    DECODE_RESPONSES,
    ENCODING,
    MAX_CONNECTIONS,
)


class Redis:
    def __init__(
            self,
            host: str,
            port: int,
            password: str,
            db: int = 0,
            decode_responses: bool = False,
            encoding: str = "utf-8",
            max_connections: int = 10,
    ):
        self.__host = host
        self.__port = port
        self.__password = password
        self.__db = db
        self.__decode_responses = decode_responses
        self.__encoding = encoding
        self.__max_connections = max_connections

        self._session: Optional[AsyncRedis] = None

    async def connect(self) -> None:
        try:
            pool: AsyncRedisConnectionPool = AsyncRedisConnectionPool(
                host=self.__host,
                port=self.__port,
                db=self.__db,
                decode_responses=self.__decode_responses,
                encoding=self.__encoding,
                max_connections=self.__max_connections,
                password=self.__password,
            )

            redis_pool: AsyncRedis = AsyncRedis(connection_pool=pool)

            self._session = redis_pool

        except Exception as error:
            await redis_error_handler(error=error)

    async def ping(self) -> Optional[Literal[True]]:
        try:
            if self._session is not None:
                await self._session.ping()
                return True

            else:
                return None

        except Exception as error:
            await redis_error_handler(error=error)

    async def get(
            self,
            key: str,
    ) -> Optional[Any]:
        try:
            if self._session is not None:
                result = await self._session.get(key)
                if result is None:
                    return None

                return pickle_loads(result)

            else:
                return None

        except Exception as error:
            await redis_error_handler(error=error)

    async def set(
            self,
            key: str,
            data: Any,
            ttl: int
    ) -> Optional[Literal[True]]:
        try:
            if self._session is not None:
                serialized_data: bytes = pickle_dumps(data)
                await self._session.set(name=key, value=serialized_data, ex=ttl)

                return True

            else:
                return None

        except Exception as error:
            await redis_error_handler(error=error)

    async def delete(self, key: str) -> Optional[Literal[True]]:
        try:
            if self._session is not None:
                await self._session.delete(key)

                return True

            else:
                return None

        except Exception as error:
            await redis_error_handler(error=error)

    async def close(self) -> Optional[Literal[True]]:
        try:
            if self._session is not None:
                await self._session.aclose(close_connection_pool=True)

                return True

            else:
                return None

        except Exception as error:
            await redis_error_handler(error=error)


redis: Redis = Redis(
    host=getenv("HMTM_BDU_REDIS_HOST", default="localhost"),
    port=int(getenv("HMTM_BDU_REDIS_PORT", default=6381)),
    password=getenv("HMTM_BDU_REDIS_PASSWORD", default=""),
    db=DB,
    decode_responses=DECODE_RESPONSES,
    encoding=ENCODING,
    max_connections=MAX_CONNECTIONS,
)
