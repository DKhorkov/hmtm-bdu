from typing import AsyncGenerator, Any

import pytest
import pytest_asyncio

from src.core.cache.redis import Redis
from src.core.cache.schemas import RedisConfig
from tests.integration.cache.constants import (
    TEST_REDIS_HOST,
    TEST_REDIS_PORT,
    TEST_REDIS_PASSWORD
)


@pytest_asyncio.fixture(scope="function")
async def mock_redis_connection() -> AsyncGenerator[Redis, Any]:
    redis: Redis = Redis(
        redis=RedisConfig(
            host=TEST_REDIS_HOST,
            port=TEST_REDIS_PORT,
            password=TEST_REDIS_PASSWORD,
            db=0,
            decode_responses=False,
            max_connections=4,
            encoding="utf-8"
        )
    )

    try:
        await redis.ping()
        yield redis

    except Exception as error:
        pytest.fail(f"REDIS_ERROR: {str(error)}")

    finally:
        await redis.close()
