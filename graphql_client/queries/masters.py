from gql import gql
from graphql import DocumentNode


class MastersCatalogQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query GetMastersCatalog($input: MastersInput) {
                    masters(input: $input) {
                        id
                        info
                        createdAt
                    }
                }
            """
        )


class MastersCounterQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query AllMastersCounter($filters: MastersFilters) {
                    mastersCounter(filters: $filters)
                }
            """
        )
