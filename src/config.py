from dotenv import load_dotenv, find_dotenv
from os import getenv
from dataclasses import dataclass

from graphql_client.client import GraphQLClient
from graphql_client.interface import GraphQLInterface
from src.enums import Environments

load_dotenv(find_dotenv())


@dataclass(frozen=True)
class Config:
    graphql_client: GraphQLInterface


config: Config

ENVIRONMENT = getenv("ENVIRONMENT")
if ENVIRONMENT == Environments.TEST:
    pass

elif ENVIRONMENT == Environments.PRODUCTION:
    pass

elif ENVIRONMENT == Environments.DEVELOPMENT:
    pass

else:
    config = Config(
        graphql_client=GraphQLClient(
            url=getenv("GRAPHQL_URL", default="http://localhost:8080/query"),
        )
    )
