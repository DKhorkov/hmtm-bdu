import io

from typing import Annotated, Dict, Optional, BinaryIO
from fastapi import Form, Request, UploadFile, File, Depends

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

    RegisterUserMutation,
    LoginUserMutation,
    VerifyUserEmailMutation,
    RefreshTokensMutation,
    SendVerifyEmailMessageMutation,
    SendForgetPasswordMessageMutation,
    ChangePasswordMutation,
    ChangeForgetPasswordMutation,
    UpdateUserProfileMutation,

    GetMeQuery,

    extract_error_message,

    ResponseProcessor as GQLResponseProcessor
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
    RefreshTokensResponse
)
from src.sso.models import User


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
) -> RefreshTokensResponse:
    result: RefreshTokensResponse = RefreshTokensResponse()

    try:
        gql_refresh_tokens: GQLResponse = await config.graphql_client.gql_query(
            query=RefreshTokensMutation.to_gql(),
            variable_values={},
            cookies=request.cookies
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
) -> GetMeResponse:
    result: GetMeResponse = GetMeResponse()

    if len(request.cookies) == 0:
        result.error = "Пользователь не найден"
        return result

    try:
        if request.cookies:
            gql_response: GQLResponse = await config.graphql_client.gql_query(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=request.cookies
            )
            if "errors" in gql_response.result:
                raise Exception

            result.user = User(
                id=gql_response.result["me"]["id"],
                display_name=gql_response.result["me"]["displayName"],
                email=gql_response.result["me"]["email"],
                email_confirmed=gql_response.result["me"]["emailConfirmed"],
                phone=gql_response.result["me"]["phone"],
                phone_confirmed=gql_response.result["me"]["phoneConfirmed"],
                telegram=gql_response.result["me"]["telegram"],
                telegram_confirmed=gql_response.result["me"]["telegramConfirmed"],
                avatar=gql_response.result["me"]["avatar"],
                created_at=gql_response.result["me"]["createdAt"],
                updated_at=gql_response.result["me"]["updatedAt"],
            )

    except Exception:
        try:
            refreshed_tokens: RefreshTokensResponse = await refresh_tokens(request)

            if refreshed_tokens.error is not None:
                result.error = refreshed_tokens.error
                return result

            result.headers = refreshed_tokens.headers
            result.cookies = refreshed_tokens.cookies

            updated_cookies: Dict[str, str] = {}
            for cookie in refreshed_tokens.cookies:
                updated_cookies[cookie.KEY] = cookie.VALUE

            gql_get_me: GQLResponse = await config.graphql_client.gql_query(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=updated_cookies
            )

            if "errors" in gql_get_me.result:
                result.error = gql_get_me.result["errors"][0]["message"]
                return result

            result.user = User(
                id=gql_get_me.result["me"]["id"],
                display_name=gql_get_me.result["me"]["displayName"],
                email=gql_get_me.result["me"]["email"],
                email_confirmed=gql_get_me.result["me"]["emailConfirmed"],
                phone=gql_get_me.result["me"]["phone"],
                phone_confirmed=gql_get_me.result["me"]["phoneConfirmed"],
                telegram=gql_get_me.result["me"]["telegram"],
                telegram_confirmed=gql_get_me.result["me"]["telegramConfirmed"],
                avatar=gql_get_me.result["me"]["avatar"],
                created_at=gql_get_me.result["me"]["createdAt"],
                updated_at=gql_get_me.result["me"]["updatedAt"],
            )

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
        old_password: Annotated[str, Form()],
        new_password: Annotated[str, Form()],
        refreshed_tokens: RefreshTokensResponse = Depends(refresh_tokens),
) -> ChangePasswordResponse:
    result: ChangePasswordResponse = ChangePasswordResponse()
    updated_cookies: Dict[str, str] = {}

    if refreshed_tokens.error is None:
        result.cookies = refreshed_tokens.cookies
        for cookie in refreshed_tokens.cookies:
            updated_cookies[cookie.KEY] = cookie.VALUE
    else:
        result.error = "Пользователь не найден"
        return result

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=ChangePasswordMutation().to_gql(),
            variable_values=ChangePasswordVariables(
                old_password=old_password,
                new_password=new_password
            ).to_dict(),
            cookies=updated_cookies,
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
        username: Annotated[str | None, Form()],
        phone: Annotated[str | None, Form()],
        telegram: Annotated[str | None, Form()],
        avatar: Annotated[UploadFile | None, File()],
        refreshed_tokens: RefreshTokensResponse = Depends(refresh_tokens),
) -> UpdateUserProfileResponse:
    result: UpdateUserProfileResponse = UpdateUserProfileResponse()
    upload_file: Optional[BinaryIO] = None
    updated_cookies: Dict[str, str] = {}

    if refreshed_tokens.error is None:
        result.cookies = refreshed_tokens.cookies
        for cookie in refreshed_tokens.cookies:
            updated_cookies[cookie.KEY] = cookie.VALUE
    else:
        result.error = "Пользователь не найден"
        return result

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
            cookies=updated_cookies,
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
