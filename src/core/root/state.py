from fastapi import Request

from graphql_client.bff_client import BFFGQLClient
from src.core.cache.redis import Redis


class GlobalAppState:

    @staticmethod
    async def bff_gql_client(request: Request) -> BFFGQLClient:
        return request.app.state.bff_gql_client  # Отдаем единый экземпляр, без создания нового

    @staticmethod
    async def redis_client(request: Request) -> Redis:
        return request.app.state.redis
