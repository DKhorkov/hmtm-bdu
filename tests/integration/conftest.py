from typing import AsyncGenerator, Any

import pytest
import pytest_asyncio

from src.cache.config import RedisConfig
from tests.integration.cache.constants import (
    TEST_REDIS_HOST,
    TEST_REDIS_PORT,
    TEST_REDIS_PASSWORD
)


@pytest_asyncio.fixture(scope="function")
async def mock_redis_connection() -> AsyncGenerator[RedisConfig, Any]:
    redis: RedisConfig = RedisConfig(
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
