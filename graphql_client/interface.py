from typing import Protocol, Dict, Any, runtime_checkable, Optional
from graphql import DocumentNode

from graphql_client.dto import GQLResponse


@runtime_checkable
class GraphQLInterface(Protocol):
    async def gql_query(
            self,
            query: DocumentNode,
            variable_values: Dict[str, Any],
            cookies: Optional[Dict[str, str]] = None
    ) -> GQLResponse:
        """Реализация запроса через клиент"""
        pass
