from typing import Optional, Dict

from fastapi import Request, Form, Depends

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.mutations.profile import UpdateMasterMutation, RegisterMasterMutation
from graphql_client.variables.profile import UpdateMasterVariables, RegisterMasterVariables
from src.core.common.dependencies import CommonAuthRedirectRepository
from src.core.common.dto import GetMeResponse
from src.core.cookies.processors import CookieProcessor
from src.core.exc.exceptions_handlers import set_error_key
from src.core.root.state import GlobalAppState
from src.domains.profile.core.dto import UpdateMasterResponse, RegisterMasterResponse
from src.domains.profile.core.schemas import GetUserWithMasterResponse
from src.domains.profile.dependencies.users import UserProfileDependenciesRepository


class MasterUserDependenciesRepository:

    @staticmethod
    async def update_master(
            request: Request,
            user_with_master: GetUserWithMasterResponse = Depends(UserProfileDependenciesRepository.user_with_master),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client),
            info: Optional[str] = Form(default=None)
    ) -> UpdateMasterResponse:
        result: UpdateMasterResponse = UpdateMasterResponse()
        actual_cookies: Dict[str, str] = CookieProcessor.get_actual_dict_cookies(
            request=request, cookies=user_with_master.cookies
        )

        if not user_with_master.master:
            set_error_key(response=result, exc="rpc error: code = Master not found")

        else:
            gql_response: GQLResponse = await gql_client.execute(
                query=UpdateMasterMutation().to_gql(),
                params=UpdateMasterVariables(
                    id=user_with_master.master.id,
                    info=info
                ).to_dict(),
                cookies=actual_cookies
            )

            if gql_response.error:
                set_error_key(response=result, exc=gql_response.error)

        return result

    @staticmethod
    async def register_master(
            request: Request,
            current_user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_not_user),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client),
            info: Optional[str] = Form(default=None)
    ) -> RegisterMasterResponse:
        result: RegisterMasterResponse = RegisterMasterResponse()
        actual_cookies: Dict[str, str] = CookieProcessor.get_actual_dict_cookies(
            request=request, cookies=current_user.cookies
        )

        gql_response: GQLResponse = await gql_client.execute(
            query=RegisterMasterMutation().to_gql(),
            params=RegisterMasterVariables(
                info=info,
            ).to_dict(),
            cookies=actual_cookies,
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result
