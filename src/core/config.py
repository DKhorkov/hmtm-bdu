from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv, find_dotenv

from os import getenv
from dataclasses import dataclass

from graphql_client.client import GraphQLClient
from graphql_client.interface import GraphQLInterface
from src.core.cache.redis import Redis
from src.core.cache.schemas import RedisConfig
from src.core.common.encryptor import Cryptography
from src.core.logger.dto import LogFormatDTO, LogsFolderDTO
from src.core.logger.logger import Logger
from src.core.logger.settings import LoggerSettings

load_dotenv(find_dotenv('.env'))

PROJECT_ROOT_FROM_CONFIG: Path = (
    Path(__file__).resolve()  # src/core/config.py
    .parent  # src/core
    .parent  # src
    .parent  # Project root
)


@dataclass(frozen=True)
class Config:
    graphql_client: GraphQLInterface
    redis_as_cache: Redis
    logger: Logger
    cryptography_key: str

    def get_encryptor(self) -> Cryptography:
        return Cryptography(secret_key=self.cryptography_key)


config: Config = Config(
    graphql_client=GraphQLClient(
        url=getenv("GRAPHQL_URL", default="http://localhost:8080/query"),
    ),
    redis_as_cache=Redis(
        redis=RedisConfig(
            host=getenv("HMTM_BDU_REDIS_HOST"),  # type: ignore
            port=getenv("HMTM_BDU_REDIS_PORT"),  # type: ignore
            password=getenv("HMTM_BDU_REDIS_PASSWORD"),  # type: ignore
            max_connections=getenv("HMTM_BDU_REDIS_MAX_CONNECTIONS")  # type: ignore
        )
    ),
    logger=Logger(
        settings=LoggerSettings(
            log_format=LogFormatDTO(),
            logs_folder=LogsFolderDTO(
                path=PROJECT_ROOT_FROM_CONFIG
            ),
        )
    ),
    cryptography_key=getenv("FERNET_KEY", default=Fernet.generate_key().decode("utf8"))
)
