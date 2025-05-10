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
                    emailConfirmed
                    phone
                    phoneConfirmed
                    telegram
                    telegramConfirmed
                    avatar
                    createdAt
                    updatedAt
                    }
                }
            """)


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
