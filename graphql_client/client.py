from typing import Dict, Any

from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode, ExecutionResult
from gql import Client

from graphql_client.dto import GQLResponse


class GraphQLClient:
    def __init__(self, url: str):
        self.__transport: AIOHTTPTransport = AIOHTTPTransport(url=url)
        self.__client: Client = Client(transport=self.__transport)

    async def gql_query(
            self,
            query: DocumentNode,
            variable_values: Dict[str, Any]
    ) -> GQLResponse:
        async with self.__client as client:
            result: Dict[str, Any] | ExecutionResult = await client.execute(
                document=query,
                variable_values=variable_values
            )

            return GQLResponse(
                result=result,
                headers=self.__transport.response_headers
            )
