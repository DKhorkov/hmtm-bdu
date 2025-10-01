from io import BytesIO
from typing import Annotated, Dict, Optional, List
from fastapi import Form, Depends, UploadFile, File
from fastapi.requests import Request

from graphql_client import extract_error_message
from graphql_client.variables.profile import (
    UpdateUserProfileVariables,
    UpdateMasterVariables,
    RegisterMasterVariables,
    GetMasterByUserVariables,
    ChangePasswordVariables
)
from graphql_client.mutations.profile import (
    ChangePasswordMutation,
    UpdateUserProfileMutation,
    UpdateMasterMutation,
    RegisterMasterMutation
)
from graphql_client.queries.profile import GetMasterByUserQuery
from graphql_client.dto import GQLResponse
from src.core.config import config
from src.core.common.constants import DEFAULT_ERROR_MESSAGE
from src.core.common.cookies import CookiesConfig
from src.core.common.dependencies import get_me
from src.domains.sso.constants import SSO_ERROR_MAPPER
from src.core.common.parsers import Parse
from src.core.common.dto import GetMeResponse
from src.domains.profile.dto import (
    UpdateUserProfileResponse,
    ChangePasswordResponse,
    GetUserIsMasterResponse,
    UpdateMasterResponse,
    RegisterMasterResponse
)
from src.domains.profile.models import Master


async def change_password(
        request: Request,
        old_password: Annotated[str, Form()],
        new_password: Annotated[str, Form()],
        current_user: GetMeResponse = Depends(get_me)
) -> ChangePasswordResponse:
    result: ChangePasswordResponse = ChangePasswordResponse()

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_response: GQLResponse = await config.graphql_client.execute(
            query=ChangePasswordMutation().to_gql(),
            variable_values=ChangePasswordVariables(
                old_password=old_password,
                new_password=new_password
            ).to_dict(),
            cookies=actual_cookies,
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки формы для смены пароля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def update_user_profile(
        request: Request,
        username: Annotated[str | None, Form()],
        phone: Annotated[str | None, Form()],
        telegram: Annotated[str | None, Form()],
        avatar: Annotated[UploadFile | None, File()],
        current_user: GetMeResponse = Depends(get_me),
) -> UpdateUserProfileResponse:
    result: UpdateUserProfileResponse = UpdateUserProfileResponse()
    upload_file: Optional[BytesIO] = None

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        if avatar and avatar.size is not None and avatar.size > 0:
            upload_file: BytesIO = BytesIO(await avatar.read())  # type: ignore
            upload_file.name = avatar.filename  # type: ignore

        gql_response: GQLResponse = await config.graphql_client.execute(
            query=UpdateUserProfileMutation().to_gql(),
            variable_values=UpdateUserProfileVariables(
                display_name=username,
                phone=phone if (phone != "Отсутствует" and phone != "") else None,
                telegram=telegram if (telegram != "Отсутствует" and telegram != "") else None,
                avatar=upload_file,
            ).to_dict(),
            upload_files=True,
            cookies=actual_cookies,
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def master_by_user(
        user_id: str,
        request: Request,
        cookies: Optional[List[CookiesConfig]] = None,
) -> GetUserIsMasterResponse:
    result: GetUserIsMasterResponse = GetUserIsMasterResponse()

    if not cookies and len(request.cookies) == 0:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if cookies:
        for cookie in cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_response: GQLResponse = await config.graphql_client.execute(
            query=GetMasterByUserQuery().to_gql(),
            variable_values=GetMasterByUserVariables(
                id=user_id,
            ).to_dict(),
            cookies=actual_cookies,
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.master = Master(
            id=gql_response.result["masterByUser"]["id"],
            info=gql_response.result["masterByUser"]["info"],
            created_at=Parse.datetime(gql_response.result["masterByUser"]["createdAt"]),
            updated_at=Parse.datetime(gql_response.result["masterByUser"]["updatedAt"]),
        )

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка получения данных о мастере"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def update_master(
        request: Request,
        info: Annotated[str | None, Form()],
        current_user: GetMeResponse = Depends(get_me),
) -> UpdateMasterResponse:
    result: UpdateMasterResponse = UpdateMasterResponse()

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        master: GetUserIsMasterResponse = await master_by_user(
            user_id=current_user.user.id,  # type: ignore[union-attr]
            request=request,
            cookies=current_user.cookies,
        )

        if master.master is None:
            raise Exception({"message": "Не удалось найти мастера"})

        gql_response: GQLResponse = await config.graphql_client.execute(
            query=UpdateMasterMutation().to_gql(),
            variable_values=UpdateMasterVariables(
                id=master.master.id,  # type: ignore[union-attr]
                info=info
            ).to_dict(),
            cookies=actual_cookies,
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0]["message"])

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения данных о мастере"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def register_master(
        request: Request,
        info: Annotated[str | None, Form()],
        current_user: GetMeResponse = Depends(get_me),
) -> RegisterMasterResponse:
    result: RegisterMasterResponse = RegisterMasterResponse()

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_response: GQLResponse = await config.graphql_client.execute(
            query=RegisterMasterMutation().to_gql(),
            variable_values=RegisterMasterVariables(
                info=info,
            ).to_dict(),
            cookies=actual_cookies,
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка при регистрации мастера"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result
