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


class RefreshTokensMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql("mutation { refreshTokens }")


class SendVerifyEmailMessageMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation SendVerifyEmailMessage($input: SendVerifyEmailMessageInput!)
                {sendVerifyEmailMessage(input: $input)}
            """
        )


class SendForgetPasswordMessageMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation SendForgetPasswordMessage($input: SendForgetPasswordMessageInput!)
                    {sendForgetPasswordMessage(input: $input)}
            """
        )


class ChangePasswordMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation ChangePassword($input: ChangePasswordInput!) {changePassword(input: $input)}
            """
        )


class ChangeForgetPasswordMutation:
    @staticmethod
    def to_gql() -> DocumentNode:
        return gql(
            """
                mutation ChangeForgetPassword($input: ForgetPasswordInput!) {forgetPassword(input: $input)}
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
