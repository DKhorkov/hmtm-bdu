from typing import Dict, Any, Optional

from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode, ExecutionResult
from gql import Client

from graphql_client.dto import GQLResponse


class GraphQLClient:
    def __init__(self, url: str) -> None:
        self.__url = url

    async def gql_query(
            self,
            query: DocumentNode,
            variable_values: Optional[Dict[str, Any]],
            cookies: Optional[Dict[str, str]] = None
    ) -> GQLResponse:
        cookies = cookies if cookies else {}
        transport = AIOHTTPTransport(url=self.__url, cookies=cookies)

        async with Client(transport=transport) as client:
            result: Dict[str, Any] | ExecutionResult = await client.execute(
                document=query,
                variable_values=variable_values
            )

            assert isinstance(result, dict)
            return GQLResponse(
                result=result,
                headers=transport.response_headers
                )
