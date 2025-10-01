from typing import Protocol, Dict, Any, runtime_checkable, Optional

from graphql import DocumentNode

from graphql_client.dto import GQLResponse


@runtime_checkable
class GraphQLInterface(Protocol):
    async def execute(
            self,
            query: DocumentNode,
            variable_values: Dict[str, Any],
            cookies: Optional[Dict[str, str]] = None,
            upload_files: bool = False
    ) -> GQLResponse:
        """Реализация запроса через клиент"""
        pass
