from fastapi import Request

from graphql_client.client import GraphQLClient
from src.core.cache.redis import Redis
from src.core.common.encryptor import Cryptography
from src.core.logger.logger import Logger


class GlobalAppState:

    @staticmethod
    async def gql_client(request: Request) -> GraphQLClient:
        return request.app.state.gql_client  # Отдаем единый экземпляр, без создания нового

    @staticmethod
    async def redis_client(request: Request) -> Redis:
        return request.app.state.redis

    @staticmethod
    async def logger(request: Request) -> Logger:
        return request.app.state.logger

    @staticmethod
    async def cryptography(request: Request) -> Cryptography:
        return request.app.state.cryptography
