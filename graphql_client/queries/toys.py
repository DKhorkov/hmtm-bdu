from gql import gql
from graphql import DocumentNode


class ToysCatalogQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query GetToysCatalog($input: ToysInput!) {
                    toys(input: $input) {
                        id
                        category {name}
                        name
                        description
                        price
                        quantity
                        createdAt
                        tags {name}
                        attachments {link}
                    }
                }
            """
        )


class ToysCounterQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query AllToysCounter($filters: ToysFilters) { toysCounter(filters: $filters) }
            """
        )


class AllToysCategoriesQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query {
                    categories {
                        id
                        name
                    }
                }
            """
        )


class AllToysTagsQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query {
                    tags {
                        id
                        name
                    }
                }
            """
        )


class ToyByIDQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query ToyByID($id: ID!) {
                    toy(id: $id) {
                        id
                        master {id user {displayName avatar}}
                        category {name}
                        name
                        description
                        price
                        quantity
                        createdAt
                        tags {name}
                        attachments {link}
                    }
                }
            """
        )
