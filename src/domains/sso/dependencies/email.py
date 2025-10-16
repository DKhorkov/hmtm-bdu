from fastapi import Depends, Form

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.mutations.sso import (
    VerifyUserEmailMutation,
    SendVerifyEmailMessageMutation
)
from graphql_client.variables.sso import (
    VerifyUserEmailVariables,
    SendVerifyEmailMessageVariables
)
from src.core.exc.exceptions_handlers import set_error_key
from src.core.state import GlobalAppState
from src.domains.sso.core.dto import (
    VerifyEmailResponse,
    SendVerifyEmailMessageResponse
)


class EmailDependenciesRepository:

    @staticmethod
    async def verify_email(
            verify_email_token: str,
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> VerifyEmailResponse:
        result: VerifyEmailResponse = VerifyEmailResponse()

        gql_response: GQLResponse = await gql_client.execute(
            query=VerifyUserEmailMutation.to_gql(),
            variable_values=VerifyUserEmailVariables(
                verify_email_token=verify_email_token,
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result

    @staticmethod
    async def send_verify_email_message(
            email: str = Form(),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> SendVerifyEmailMessageResponse:
        result: SendVerifyEmailMessageResponse = SendVerifyEmailMessageResponse(email=email)

        gql_response: GQLResponse = await gql_client.execute(
            query=SendVerifyEmailMessageMutation().to_gql(),
            variable_values=SendVerifyEmailMessageVariables(
                email=email
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result
