from gql import gql
from graphql import DocumentNode


class ChangePasswordMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation ChangePassword($input: ChangePasswordInput!) {changePassword(input: $input)}
            """
        )


class UpdateUserProfileMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation UpdateUserProfile($input: UpdateUserProfileInput!) {updateUserProfile(input: $input)}
            """
        )


class UpdateMasterMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation UpdateMaster($input: UpdateMasterInput!) {updateMaster(input: $input)}
            """
        )


class RegisterMasterMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation RegisterMaster($input: RegisterMasterInput!) {registerMaster(input: $input)}
            """
        )
