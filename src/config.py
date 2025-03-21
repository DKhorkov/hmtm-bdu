from dotenv import load_dotenv, find_dotenv
from os import getenv
from dataclasses import dataclass

from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

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
            Client(
                transport=AIOHTTPTransport(
                    url=getenv("GRAPHQL_URL", default="")
                )
            )
        )
    )
