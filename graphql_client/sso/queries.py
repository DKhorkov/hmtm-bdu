from gql import gql
from graphql import DocumentNode


class GetMeQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql("""
            query {
                me {
                    id
                    displayName
                    email
                    }
                }
            """)
