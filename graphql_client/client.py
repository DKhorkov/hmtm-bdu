from typing import Dict, Any

from graphql import DocumentNode, ExecutionResult
from gql import Client


class GraphQLClient:
    def __init__(self, client: Client):
        self.__client: Client = client

    async def gql_query(
            self,
            query: DocumentNode,
            variable_values: Dict[str, Any]
    ) -> Dict[str, Any] | ExecutionResult:
        async with self.__client as client:
            return await client.execute(document=query, variable_values=variable_values)
