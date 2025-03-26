from gql import gql
from graphql import DocumentNode


class RegisterUserMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql("mutation RegisterUser($input: RegisterUserInput!) {registerUser(input: $input)}")


class LoginUserMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql("mutation LoginUser($input: LoginUserInput!) {loginUser(input: $input)}")


class VerifyUserEmailMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql("mutation VerifyUserEmail($input: VerifyUserEmailInput!) {verifyUserEmail(input: $input)}")
