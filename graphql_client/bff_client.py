from typing import Dict, Any, Optional

from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode, ExecutionResult
from gql import Client

from graphql_client.constants import GQL_SERVER_ERROR
from graphql_client.dto import GQLResponse
from aiohttp import ServerDisconnectedError, ClientConnectionError

from src.core.logger import logger
from src.core.logger.enums import Levels


class BFFGQLClient:
    def __init__(self, url: str) -> None:
        self.__url = url

    async def execute(
            self,
            query: DocumentNode,
            params: Optional[Dict[str, Any]],
            cookies: Optional[Dict[str, str]] = None,
            upload_files: bool = False,
    ) -> GQLResponse:
        cookies = cookies if cookies else {}
        transport = AIOHTTPTransport(url=self.__url, cookies=cookies)
        result: GQLResponse = GQLResponse()

        async with Client(transport=transport) as client:
            try:
                gql_response: Dict[str, Any] | ExecutionResult = await client.execute(
                    document=query,
                    variable_values=params,
                    upload_files=upload_files
                )

                assert isinstance(gql_response, dict)

                result.result = gql_response
                result.headers = transport.response_headers

            except Exception as error:
                if isinstance(error, (ServerDisconnectedError, ClientConnectionError)):
                    await logger.write(
                        level=Levels.CRITICAL,
                        message=f"GQL_SERVER_ERROR | {error}",
                    )
                    result.error = f"{GQL_SERVER_ERROR}: {str(error)}"

                else:
                    result.error = str(error)

        return result
