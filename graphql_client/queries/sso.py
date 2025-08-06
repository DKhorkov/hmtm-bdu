from gql import gql
from graphql import DocumentNode


class GetUserByIDQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query GetUserByID($id: ID!) {
                    user(id: $id) {
                        id
                        displayName
                        email
                        phone
                        telegram
                        avatar
                        createdAt
                    }
                }
            """
        )


class GetUserByEmailQuery:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                query GetUserByEmail($email: String!) {
                    userByEmail(email: $email) {
                        id
                        displayName
                        email
                        phone
                        telegram
                        avatar
                        createdAt
                    }
                }
            """
        )
