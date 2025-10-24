from typing import Optional

from fastapi import Request, Depends, Form

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.mutations.sso import ChangeForgetPasswordMutation, SendForgetPasswordMessageMutation
from graphql_client.variables.sso import ForgetPasswordVariables, SendForgetPasswordMessageVariables
from src.core.exc.exceptions_handlers import set_error_key
from src.core.state import GlobalAppState
from src.domains.sso.core.constants import FORGET_PASSWORD_TOKEN_NAME
from src.domains.sso.core.dto import ChangeForgetPasswordResponse, SendForgetPasswordMessageResponse


class PasswordDependenciesRepository:

    @staticmethod
    async def send_forget_password_message(
            email: str = Form(),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> SendForgetPasswordMessageResponse:
        result: SendForgetPasswordMessageResponse = SendForgetPasswordMessageResponse()

        gql_response: GQLResponse = await gql_client.execute(
            query=SendForgetPasswordMessageMutation().to_gql(),
            params=SendForgetPasswordMessageVariables(
                email=email
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result

    @staticmethod
    async def change_forget_password(
            request: Request,
            new_password: str = Form(),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> ChangeForgetPasswordResponse:
        result: ChangeForgetPasswordResponse = ChangeForgetPasswordResponse()

        forget_password_token: Optional[str] = request.cookies.get(FORGET_PASSWORD_TOKEN_NAME)
        if forget_password_token is None:
            result.error = "4200"
            return result

        gql_response: GQLResponse = await gql_client.execute(
            query=ChangeForgetPasswordMutation().to_gql(),
            params=ForgetPasswordVariables(
                forget_password_token=forget_password_token,
                new_password=new_password
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result
