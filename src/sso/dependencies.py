import io

from typing import Annotated, Dict, Optional, BinaryIO, List
from fastapi import Form, Request, UploadFile, File, Depends

from src.cookies import CookiesConfig
from src.sso.datetime_parser import DatetimeParser
from graphql_client.dto import GQLResponse
from src.config import config
from src.sso.constants import ERRORS_MAPPING, FORGET_PASSWORD_TOKEN_NAME
from src.constants import DEFAULT_ERROR_MESSAGE
from graphql_client import (
    RegisterUserVariables,
    LoginUserVariables,
    VerifyUserEmailVariables,
    SendVerifyEmailMessageVariables,
    SendForgetPasswordMessageVariables,
    ChangePasswordVariables,
    ForgetPasswordVariables,
    UpdateUserProfileVariables,
    UpdateMasterVariables,
    RegisterMasterVariables,
    GetMasterByUserVariables,
    GetUserByIDVariables,

    RegisterUserMutation,
    LoginUserMutation,
    VerifyUserEmailMutation,
    RefreshTokensMutation,
    SendVerifyEmailMessageMutation,
    SendForgetPasswordMessageMutation,
    ChangePasswordMutation,
    ChangeForgetPasswordMutation,
    UpdateUserProfileMutation,
    UpdateMasterMutation,
    RegisterMasterMutation,
    GetUserByIDQuery,

    GetMeQuery,
    GetMasterByUserQuery,

    extract_error_message,

    ResponseProcessor as GQLResponseProcessor,
)
from src.sso.dto import (
    LoginResponse,
    GetMeResponse,
    RegisterResponse,
    VerifyEmailResponse,
    SendVerifyEmailMessageResponse,
    SendForgetPasswordMessageResponse,
    ChangePasswordResponse,
    ChangeForgetPasswordResponse,
    UpdateUserProfileResponse,
    RefreshTokensResponse,
    GetUserIsMasterResponse,
    UpdateMasterResponse,
    RegisterMasterResponse,
    GetAllUserInfoByIDResponse,
)
from src.sso.models import Master, UserInfoByID
from src.sso.utils import user_from_dict


async def process_register(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        display_name: Annotated[str, Form()]
) -> RegisterResponse:
    result: RegisterResponse = RegisterResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=RegisterUserMutation.to_gql(),
            variable_values=RegisterUserVariables(
                display_name=display_name,
                email=email,
                password=password
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка регистрации"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def process_login(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()]
) -> LoginResponse:
    result: LoginResponse = LoginResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=LoginUserMutation.to_gql(),
            variable_values=LoginUserVariables(
                email=email,
                password=password
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

        if gql_response.headers is not None:
            result.cookies = GQLResponseProcessor(gql_response=gql_response).get_cookies()

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка аутентификации"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def verify_email(  # type: ignore[return]
        verify_email_token: str
) -> VerifyEmailResponse:
    result: VerifyEmailResponse = VerifyEmailResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=VerifyUserEmailMutation.to_gql(),
            variable_values=VerifyUserEmailVariables(
                verify_email_token=verify_email_token,
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка подтверждения email"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def refresh_tokens(
        request: Request,
        cookies: Optional[List[CookiesConfig]] = None
) -> RefreshTokensResponse:
    result: RefreshTokensResponse = RefreshTokensResponse()

    actual_cookies: Dict[str, str] = request.cookies
    if cookies:
        for cookie in cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_refresh_tokens: GQLResponse = await config.graphql_client.gql_query(
            query=RefreshTokensMutation.to_gql(),
            variable_values={},
            cookies=actual_cookies
        )

        if "errors" in gql_refresh_tokens.result:
            result.error = gql_refresh_tokens.result["errors"][0]["message"]
            return result

        result.result = True
        result.headers = gql_refresh_tokens.headers  # type: ignore[assignment]

        if gql_refresh_tokens.headers is not None:
            result.cookies = GQLResponseProcessor(gql_response=gql_refresh_tokens).get_cookies()

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка обновления токенов"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def get_me(
        request: Request,
        cookies: Optional[List[CookiesConfig]] = None
) -> GetMeResponse:
    result: GetMeResponse = GetMeResponse()

    if not cookies and len(request.cookies) == 0:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if cookies:
        for cookie in cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        if request.cookies:
            gql_response: GQLResponse = await config.graphql_client.gql_query(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=actual_cookies
            )
            if "errors" in gql_response.result:
                raise Exception

            result.user = user_from_dict(gql_response.result["me"])

    except Exception:
        try:
            refreshed_tokens: RefreshTokensResponse = await refresh_tokens(request=request, cookies=cookies)

            if refreshed_tokens.error is not None:
                result.error = refreshed_tokens.error
                return result

            result.headers = refreshed_tokens.headers
            result.cookies = refreshed_tokens.cookies

            actual_cookies = {}
            for cookie in refreshed_tokens.cookies:
                actual_cookies[cookie.KEY] = cookie.VALUE

            gql_get_me: GQLResponse = await config.graphql_client.gql_query(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=actual_cookies
            )

            if "errors" in gql_get_me.result:
                result.error = gql_get_me.result["errors"][0]["message"]
                return result

            result.user = user_from_dict(gql_get_me.result["me"])

        except Exception as err:
            error = ERRORS_MAPPING.get(
                extract_error_message(
                    error=str(err),
                    default_message="Ошибка проверки cookies"
                ),
                DEFAULT_ERROR_MESSAGE
            )
            result.error = error

    return result


async def send_verify_email_message(
        email: Annotated[str, Form()]
) -> SendVerifyEmailMessageResponse:
    result: SendVerifyEmailMessageResponse = SendVerifyEmailMessageResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=SendVerifyEmailMessageMutation().to_gql(),
            variable_values=SendVerifyEmailMessageVariables(
                email=email
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки письма подтверждения электронной почты"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def send_forget_password_message(
        email: Annotated[str, Form()]
) -> SendForgetPasswordMessageResponse:
    result: SendForgetPasswordMessageResponse = SendForgetPasswordMessageResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=SendForgetPasswordMessageMutation().to_gql(),
            variable_values=SendForgetPasswordMessageVariables(
                email=email
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки письма для восстановления забытого пароля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def change_forget_password(
        request: Request,
        new_password: Annotated[str, Form()]
) -> ChangeForgetPasswordResponse:
    result: ChangeForgetPasswordResponse = ChangeForgetPasswordResponse()
    try:
        forget_password_token: Optional[str] = request.cookies.get(FORGET_PASSWORD_TOKEN_NAME)
        if forget_password_token is None:
            result.error = "Ошибка: Токен не найден, попробуйте перейти по ссылке из письма повторно"
            return result

        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=ChangeForgetPasswordMutation().to_gql(),
            variable_values=ForgetPasswordVariables(
                forget_password_token=forget_password_token,
                new_password=new_password
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки формы для смены забытого пароля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


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
        gql_response: GQLResponse = await config.graphql_client.gql_query(
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
        error: str = ERRORS_MAPPING.get(
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
    upload_file: Optional[BinaryIO] = None

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
            upload_file = io.BytesIO(await avatar.read())
            upload_file.name = avatar.filename

        gql_response: GQLResponse = await config.graphql_client.gql_query(
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
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def master_by_user(
        user_id: int,
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
        gql_response: GQLResponse = await config.graphql_client.gql_query(
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
            created_at=DatetimeParser.parse(gql_response.result["masterByUser"]["createdAt"]),
            updated_at=DatetimeParser.parse(gql_response.result["masterByUser"]["updatedAt"]),
        )

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
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
            result.error = "Не удалось найти мастера"
            return result

        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=UpdateMasterMutation().to_gql(),
            variable_values=UpdateMasterVariables(
                id=master.master.id,
                info=info
            ).to_dict(),
            cookies=actual_cookies,
        )

        if "errors" in gql_response.result:
            result.error = gql_response.result["errors"][0]["message"]
            return result

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
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
        gql_response: GQLResponse = await config.graphql_client.gql_query(
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
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def user_info_by_id(
        user_id: int,
) -> GetAllUserInfoByIDResponse:
    result: GetAllUserInfoByIDResponse = GetAllUserInfoByIDResponse(errors=[])

    try:
        user: GQLResponse = await config.graphql_client.gql_query(
            query=GetUserByIDQuery().to_gql(),
            variable_values=GetUserByIDVariables(
                id=user_id,
            ).to_dict(),
        )

        if "errors" in user.result:
            raise Exception(user.result["errors"][0])

        result.user = UserInfoByID(
            display_name=user.result["user"]["displayName"],
            email=user.result["user"]["email"],
            phone=user.result["user"]["phone"],
            telegram=user.result["user"]["telegram"],
            avatar=user.result["user"]["avatar"],
            created_at=DatetimeParser.parse(user.result["user"]["createdAt"]),
        )

        master: GQLResponse = await config.graphql_client.gql_query(
            query=GetMasterByUserQuery().to_gql(),
            variable_values=GetMasterByUserVariables(
                id=user_id,
            ).to_dict(),
        )

        if "errors" not in master.result:
            result.master = Master(
                id=master.result["masterByUser"]["id"],
                info=master.result["masterByUser"]["info"],
                created_at=DatetimeParser.parse(master.result["masterByUser"]["createdAt"]),
                updated_at=DatetimeParser.parse(master.result["masterByUser"]["updatedAt"]),
            )
        else:
            result.errors.append(master.result["errors"][0]["message"])  # type: ignore[union-attr]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.errors.append(error)  # type: ignore[union-attr]

    return result
