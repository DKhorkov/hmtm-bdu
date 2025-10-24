from dotenv import load_dotenv, find_dotenv

from os import getenv
from dataclasses import dataclass

from graphql_client.bff_client import BFFGQLClient
from src.core.cache.redis import Redis
from src.core.cache.schemas import RedisConfig

load_dotenv(find_dotenv('.env'))


@dataclass(frozen=True)
class Config:
    bff_gql_client: BFFGQLClient
    redis_as_cache: Redis


config: Config = Config(
    bff_gql_client=BFFGQLClient(
        url=getenv("GRAPHQL_URL", default="http://localhost:8080/query"),
    ),
    redis_as_cache=Redis(
        redis=RedisConfig(
            host=getenv("HMTM_BDU_REDIS_HOST"),  # type: ignore
            port=getenv("HMTM_BDU_REDIS_PORT"),  # type: ignore
            password=getenv("HMTM_BDU_REDIS_PASSWORD"),  # type: ignore
            max_connections=getenv("HMTM_BDU_REDIS_MAX_CONNECTIONS")  # type: ignore
        )  # Игнорирование типов -> автосериализация за счет pydantic-моделей
    )
)