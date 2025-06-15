from os import getenv
from typing import Any, Optional, Literal
from pickle import loads as pickle_loads, dumps as pickle_dumps

from dotenv import load_dotenv, find_dotenv

from redis.asyncio import (
    Redis as AsyncRedis,
    ConnectionPool as AsyncRedisConnectionPool
)
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
    AuthenticationError as RedisAuthenticationError,
)

from src.logging.config import logger
from src.logging.enums import Levels
from src.cache.constants import REDIS_CONNECTION_ERROR, REDIS_AUTHENTICATION_ERROR


class RedisConfig:
    load_dotenv(find_dotenv(".env"))

    def __init__(
            self,
            host: str = getenv("HMTM_BDU_REDIS_HOST", default="localhost"),
            port: int = int(getenv("HMTM_BDU_REDIS_PORT", default=6381)),
            password: str = getenv("HMTM_BDU_REDIS_PASSWORD", default="")
    ):
        self.__host = host
        self.__port = port
        self.__password = password
        self._session: Optional[AsyncRedis] = None

    async def connect(self) -> Optional[Literal[True]]:
        try:
            pool: AsyncRedisConnectionPool = AsyncRedisConnectionPool(
                # Main
                host=self.__host,
                port=self.__port,
                db=0,
                # Encode/decode:
                decode_responses=False,
                encoding="utf-8",
                # Pools:
                max_connections=10,
                # Secure:
                password=self.__password,
            )

            redis: AsyncRedis = AsyncRedis(connection_pool=pool)
            await redis.ping()

            self._session = redis

            return True

        except RedisAuthenticationError:
            raise RedisAuthenticationError(REDIS_AUTHENTICATION_ERROR)

        except RedisConnectionError:
            raise RedisConnectionError(REDIS_CONNECTION_ERROR)

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

        except RedisConnectionError:
            await logger(level=Levels.CRITICAL, message=REDIS_CONNECTION_ERROR)
            raise RedisConnectionError(REDIS_CONNECTION_ERROR)

        except Exception as error:
            await logger(level=Levels.ERROR, message=str(error))
            return None

    async def set(
            self,
            key: str,
            data: Any,
            ttl_per_seconds: int
    ) -> Optional[Literal[True]]:
        try:
            if self._session is not None:
                serialized_data: bytes = pickle_dumps(data)
                await self._session.set(name=key, value=serialized_data, ex=ttl_per_seconds)

                return True

            else:
                return None

        except RedisConnectionError:
            await logger(level=Levels.CRITICAL, message=REDIS_CONNECTION_ERROR)
            raise RedisConnectionError(REDIS_CONNECTION_ERROR)

        except Exception as error:
            await logger(level=Levels.ERROR, message=str(error))
            return None

    async def delete(self, key: str) -> Optional[Literal[True]]:
        try:
            if self._session is not None:
                await self._session.delete(key)

                return True

            else:
                return None

        except RedisConnectionError:
            await logger(level=Levels.CRITICAL, message=REDIS_CONNECTION_ERROR)
            raise RedisConnectionError(REDIS_CONNECTION_ERROR)

        except Exception as error:
            await logger(level=Levels.ERROR, message=str(error))
            return None

    async def close(self) -> Optional[Literal[True]]:
        try:
            if self._session is not None:
                await self._session.aclose(close_connection_pool=True)

                return True

            else:
                return None

        except RedisConnectionError:
            await logger(level=Levels.CRITICAL, message=REDIS_CONNECTION_ERROR)
            raise RedisConnectionError(REDIS_CONNECTION_ERROR)

        except Exception as error:
            await logger(level=Levels.ERROR, message=str(error))
            return None
