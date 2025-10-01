from typing import Dict, Any, Optional
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode, ExecutionResult, print_ast
from gql import Client
from graphql_client.dto import GQLResponse
from aiohttp import ServerDisconnectedError

from src.core.logger.enums import Levels


class GraphQLClient:
    def __init__(self, url: str) -> None:
        self.__url = url

    async def execute(
            self,
            query: DocumentNode,
            variable_values: Optional[Dict[str, Any]],
            cookies: Optional[Dict[str, str]] = None,
            upload_files: bool = False
    ) -> GQLResponse:
        cookies = cookies if cookies else {}
        transport = AIOHTTPTransport(url=self.__url, cookies=cookies)

        async with Client(transport=transport) as client:
            try:
                result: Dict[str, Any] | ExecutionResult = await client.execute(
                    document=query,
                    variable_values=variable_values,
                    upload_files=upload_files
                )

                assert isinstance(result, dict)
                return GQLResponse(
                    result=result,
                    headers=transport.response_headers
                )

            except ServerDisconnectedError as error:
                from src.core.config import config  # Ленивая загрузка. Решает проблему циклическим импортов

                await config.logger.write_log(
                    level=Levels.CRITICAL,
                    message=f"ServerDisconnectedError | Query: {print_ast(query)}",
                )
                raise error

            except Exception as error:
                raise error
