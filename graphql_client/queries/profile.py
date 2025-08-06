from gql import gql
from graphql import DocumentNode


class GetMasterByUserQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query MasterByUser($userId: ID!) {
                    masterByUser(userId: $userId) {
                        id
                        user {
                            id
                        }
                        info
                        createdAt
                        updatedAt
                        }
                }
            """
        )
