from io import BytesIO
from typing import Optional, Dict

from fastapi import Request, Form, UploadFile, File, Depends

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.mutations.profile import UpdateUserProfileMutation
from graphql_client.queries.profile import GetMasterByUserQuery
from graphql_client.variables.profile import UpdateUserProfileVariables, GetMasterByUserVariables
from src.core.common.dependencies import CommonAuthRedirectRepository
from src.core.common.dto import GetMeResponse
from src.core.common.parsers import ModelParser
from src.core.cookies.processors import CookieProcessor
from src.core.exc.exceptions_handlers import set_error_key
from src.core.state import GlobalAppState
from src.domains.profile.core.constants import DEFAULT_PROFILE_ATTR_VALUE
from src.domains.profile.core.dto import UpdateUserProfileResponse
from src.domains.profile.core.schemas import GetUserWithMasterResponse


class UserProfileDependenciesRepository:

    @staticmethod
    async def update_user_profile(
            request: Request,
            current_user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_not_user),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client),
            username: Optional[str] = Form(default=None),
            phone: Optional[str] = Form(default=None),
            telegram: Optional[str] = Form(default=None),
            avatar: Optional[UploadFile] = File(default=None)
    ) -> UpdateUserProfileResponse:
        result: UpdateUserProfileResponse = UpdateUserProfileResponse()
        actual_cookies: Dict[str, str] = CookieProcessor.get_actual_dict_cookies(
            request=request, cookies=current_user.cookies
        )

        upload_file: Optional[BytesIO] = None
        if avatar and avatar.size and avatar.size > 0:
            upload_file: BytesIO = BytesIO(await avatar.read())  # type: ignore
            upload_file.name = avatar.filename  # type: ignore

        gql_response: GQLResponse = await gql_client.execute(
            query=UpdateUserProfileMutation().to_gql(),
            params=UpdateUserProfileVariables(
                display_name=username,
                phone=phone if phone and phone != DEFAULT_PROFILE_ATTR_VALUE else None,
                telegram=telegram if telegram and telegram != DEFAULT_PROFILE_ATTR_VALUE else None,
                avatar=upload_file,
            ).to_dict(),
            upload_files=True,
            cookies=actual_cookies,
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        return result

    @staticmethod
    async def user_with_master(
            request: Request,
            current_user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_not_user),
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> GetUserWithMasterResponse:
        result: GetUserWithMasterResponse = GetUserWithMasterResponse()
        actual_cookies: Dict[str, str] = CookieProcessor.get_actual_dict_cookies(
            request=request, cookies=current_user.cookies
        )

        gql_response: GQLResponse = await gql_client.execute(
            query=GetMasterByUserQuery().to_gql(),
            params=GetMasterByUserVariables(
                id=current_user.user.id,  # type: ignore
            ).to_dict(),
            cookies=actual_cookies,
        )

        if gql_response.error:
            result.error = gql_response.error

        else:
            result.master = ModelParser.master_from_dict(gql_response.result["masterByUser"])

        result.user = current_user.user
        result.cookies = current_user.cookies

        return result
