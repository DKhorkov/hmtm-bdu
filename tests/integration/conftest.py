from typing import AsyncGenerator, Any

import pytest
import pytest_asyncio

from src.cache.redis import Redis
from tests.integration.cache.constants import (
    TEST_REDIS_HOST,
    TEST_REDIS_PORT,
    TEST_REDIS_PASSWORD
)


@pytest_asyncio.fixture(scope="function")
async def mock_redis_connection() -> AsyncGenerator[Redis, Any]:
    redis: Redis = Redis(
        host=TEST_REDIS_HOST,
        port=TEST_REDIS_PORT,
        password=TEST_REDIS_PASSWORD
    )

    try:
        await redis.connect()
        yield redis

    except Exception as error:
        pytest.fail(f"REDIS_ERROR: {str(error)}")

    finally:
        await redis.close()
