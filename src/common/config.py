from dotenv import load_dotenv, find_dotenv

from os import getenv
from dataclasses import dataclass

from graphql_client.client import GraphQLClient
from graphql_client.interface import GraphQLInterface
from src.common.enums import Environments

load_dotenv(find_dotenv('.env'))


@dataclass(frozen=True)
class Config:
    graphql_client: GraphQLInterface


config: Config = Config(
    graphql_client=GraphQLClient(
        url=getenv("GRAPHQL_URL", default="http://localhost:8080/query"),
    )
)

ENVIRONMENT = getenv("ENVIRONMENT")
if ENVIRONMENT == Environments.TEST:
    pass

elif ENVIRONMENT == Environments.PRODUCTION:
    pass

elif ENVIRONMENT == Environments.DEVELOPMENT:
    pass
