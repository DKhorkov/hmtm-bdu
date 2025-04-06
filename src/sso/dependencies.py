from typing import Annotated, Dict

from fastapi import Form, Request

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
    # ChangePasswordVariables,
    ForgetPasswordVariables,

    RegisterUserMutation,
    LoginUserMutation,
    VerifyUserEmailMutation,
    RefreshTokensMutation,
    SendVerifyEmailMessageMutation,
    SendForgetPasswordMessageMutation,
    # ChangePasswordMutation,
    ChangeForgetPasswordMutation,

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
    # ChangePasswordResponse,
    ChangeForgetPasswordResponse,
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
        password: Annotated[str, Form()],
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


async def get_me(
        request: Request,
) -> GetMeResponse:
    result: GetMeResponse = GetMeResponse()

    if len(request.cookies) == 0:
        result.error = "AccessToken не найден"
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
                email=gql_response.result["me"]["email"],
                display_name=gql_response.result["me"]["displayName"],
            )

    except Exception:
        try:
            gql_refresh_tokens: GQLResponse = await config.graphql_client.gql_query(
                query=RefreshTokensMutation.to_gql(),
                variable_values={},
                cookies=request.cookies
            )

            if "errors" in gql_refresh_tokens.result:
                result.error = gql_refresh_tokens.result["errors"][0]["message"]
                return result

            result.headers = gql_refresh_tokens.headers  # type: ignore[assignment]

            if gql_refresh_tokens.headers is not None:
                result.cookies = GQLResponseProcessor(gql_response=gql_refresh_tokens).get_cookies()

            updated_cookies: Dict[str, str] = {}
            for cookie in result.cookies:
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
                email=gql_get_me.result["me"]["email"],
                display_name=gql_get_me.result["me"]["displayName"],
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
):
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
):
    result: ChangeForgetPasswordResponse = ChangeForgetPasswordResponse()

    try:
        forget_password_token: str = request.cookies[FORGET_PASSWORD_TOKEN_NAME]

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
