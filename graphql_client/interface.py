from typing import Protocol, Dict, Any, runtime_checkable
from graphql import DocumentNode, ExecutionResult


@runtime_checkable
class GraphQLInterface(Protocol):
    async def gql_query(
            self,
            query: DocumentNode,
            variable_values: Dict[str, Any]
    ) -> Dict[str, Any] | ExecutionResult:
        """Реализация запроса через клиент"""
        pass
