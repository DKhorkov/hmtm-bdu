import pytest

pytestmark = pytest.mark.usefixtures("mock_redis_connection")

from unittest.mock import MagicMock

from fastapi import Request


from src.core.cache.ttl_dto import CacheTTL
from src.core.cache.redis import Redis
from tests.integration.cache.constants import (
    TEST_REDIS_KEY,
    TEST_REDIS_RETURN_VALUE,
)


@pytest.mark.mock_redis_connection
class TestRedis:
    @pytest.mark.asyncio
    async def test_redis_success(self, mock_redis_connection: Redis):
        assert mock_redis_connection._redis is not None

        mock_request = MagicMock(spec=Request)
        await mock_redis_connection.set(
            key=TEST_REDIS_KEY,
            data=TEST_REDIS_RETURN_VALUE,
            ttl=CacheTTL.TEST.ONE_MINUTE,
        )

        get_redis_data = await mock_redis_connection.get(key=TEST_REDIS_KEY)
        assert get_redis_data == TEST_REDIS_RETURN_VALUE

        await mock_redis_connection.delete(key=TEST_REDIS_KEY)

    @pytest.mark.asyncio
    async def test_get_empty_redis_data(self, mock_redis_connection: Redis):
        assert mock_redis_connection._redis is not None

        mock_request = MagicMock(spec=Request)
        get_redis_data = await mock_redis_connection.get(key=TEST_REDIS_KEY)
        assert get_redis_data is None
