from fastapi import Form, Depends

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.mutations.sso import RegisterUserMutation, LoginUserMutation
from graphql_client.variables.sso import RegisterUserVariables, LoginUserVariables
from src.core.common.dependencies import CommonAuthRedirectRepository
from src.core.common.dto import GetMeResponse
from src.core.cookies.processors import CookieProcessor
from src.core.exc.exceptions_handlers import set_error_key
from src.core.state import GlobalAppState
from src.domains.sso.core.dto import RegisterResponse, LoginResponse


class AuthDependenciesRepository:

    @staticmethod
    async def process_register(
            email: str = Form(),
            password: str = Form(),
            display_name: str = Form(),
            user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_user),  # noqa
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> RegisterResponse:
        result: RegisterResponse = RegisterResponse(display_name=display_name, email=email)

        gql_response: GQLResponse = await gql_client.execute(
            query=RegisterUserMutation.to_gql(),
            params=RegisterUserVariables(
                display_name=display_name,
                email=email,
                password=password
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result

    @staticmethod
    async def process_login(
            email: str = Form(),
            password: str = Form(),
            user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_user),  # noqa
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> LoginResponse:
        result: LoginResponse = LoginResponse(email=email)

        gql_response: GQLResponse = await gql_client.execute(
            query=LoginUserMutation.to_gql(),
            params=LoginUserVariables(
                email=email,
                password=password
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        result.cookies = CookieProcessor.get_cookies_from_gql_headers(response_headers=gql_response.headers)

        return result
