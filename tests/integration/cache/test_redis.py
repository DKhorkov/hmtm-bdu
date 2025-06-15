import pytest

pytestmark = pytest.mark.usefixtures("mock_redis_connection")

from tests.integration.cache.constants import (
    TEST_REDIS_KEY,
    TEST_REDIS_RETURN_VALUE,
)
from src.cache.config import RedisConfig


class TestRedisConfig:
    @pytest.mark.redis
    @pytest.mark.asyncio
    async def test_redis_success(self, mock_redis_connection: RedisConfig):
        assert mock_redis_connection._session is not None

        set_redis_data = await mock_redis_connection.set(
            key=TEST_REDIS_KEY,
            data=TEST_REDIS_RETURN_VALUE,
            ttl_per_seconds=60
        )
        assert set_redis_data is True

        get_redis_data = await mock_redis_connection.get(key=TEST_REDIS_KEY)
        assert get_redis_data == TEST_REDIS_RETURN_VALUE

        delete_redis_data = await mock_redis_connection.delete(key=TEST_REDIS_KEY)
        assert delete_redis_data is True

    @pytest.mark.redis
    @pytest.mark.asyncio
    async def test_get_empty_redis_data(self, mock_redis_connection: RedisConfig):
        assert mock_redis_connection._session is not None

        get_redis_data = await mock_redis_connection.get(key=TEST_REDIS_KEY)
        assert get_redis_data is None
