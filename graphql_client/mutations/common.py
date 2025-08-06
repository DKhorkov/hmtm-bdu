from gql import gql
from graphql import DocumentNode


class RefreshTokensMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql("mutation { refreshTokens }")
