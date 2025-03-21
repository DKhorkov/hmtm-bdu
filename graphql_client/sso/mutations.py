from gql import gql
from graphql import DocumentNode


class RegisterUserQuery:
    @staticmethod
    def mutation() -> DocumentNode:
        return gql("mutation RegisterUser($input: RegisterUserInput!) {registerUser(input: $input)}")


class LoginUserQuery:
    @staticmethod
    def mutation() -> DocumentNode:
        return gql("mutation LoginUser($input: LoginUserInput!) {loginUser(input: $input)}")


class VerifyUserEmailQuery:
    @staticmethod
    def mutation() -> DocumentNode:
        return gql("mutation VerifyUserEmail($input: VerifyUserEmailInput!) {verifyUserEmail(input: $input)}")
