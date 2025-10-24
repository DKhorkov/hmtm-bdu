from typing import Dict

from fastapi import Request, Form, Depends

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.mutations.profile import ChangePasswordMutation
from graphql_client.variables.profile import ChangePasswordVariables
from src.core.common.dependencies import CommonAuthRedirectRepository
from src.core.common.dto import GetMeResponse
from src.core.cookies.processors import CookieProcessor
from src.core.exc.exceptions_handlers import set_error_key
from src.core.state import GlobalAppState
from src.domains.profile.core.dto import ChangePasswordResponse


class PasswordDependenciesRepository:

    @staticmethod
    async def change_password(
            request: Request,
            old_password: str = Form(),
            new_password: str = Form(),
            current_user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_not_user),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> ChangePasswordResponse:
        result: ChangePasswordResponse = ChangePasswordResponse()
        actual_cookies: Dict[str, str] = CookieProcessor.get_actual_dict_cookies(
            request=request, cookies=current_user.cookies
        )
        result.cookies = current_user.cookies

        gql_response: GQLResponse = await gql_client.execute(
            query=ChangePasswordMutation().to_gql(),
            params=ChangePasswordVariables(
                old_password=old_password,
                new_password=new_password
            ).to_dict(),
            cookies=actual_cookies,
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result
