from typing import Optional, Annotated, List

from fastapi import Form, Request

from graphql_client.cookie import Cookie as GQLCookie, CookiesParser
from src.config import config
from src.cookies import CookiesConfig
from src.sso.constants import ERRORS_MAPPING
from src.constants import DEFAULT_ERROR_MESSAGE
from graphql_client import (
    RegisterUserVariables,
    LoginUserVariables,
    VerifyUserEmailVariables,

    RegisterUserMutation,
    LoginUserMutation,
    VerifyUserEmailMutation,

    GetMeQuery,

    extract_error_message
)
from src.sso.dto import LoginResponse, GetMeResponse
from src.sso.models import User


async def process_register(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        display_name: Annotated[str, Form()]
) -> Optional[str]:
    try:
        await config.graphql_client.gql_query(
            query=RegisterUserMutation.to_gql(),
            variable_values=RegisterUserVariables(
                display_name=display_name,
                email=email,
                password=password
            ).to_dict()
        )

    except Exception as error:
        return ERRORS_MAPPING.get(
            extract_error_message(
                error=str(error),
                default_message="Ошибка регистрации"
            ),
            DEFAULT_ERROR_MESSAGE
        )


async def process_login(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
) -> LoginResponse:
    result: LoginResponse = LoginResponse()
    try:
        gql_response = await config.graphql_client.gql_query(
            query=LoginUserMutation.to_gql(),
            variable_values=LoginUserVariables(
                email=email,
                password=password
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers

        if gql_response.headers is not None:
            gql_cookies: List[GQLCookie] = CookiesParser.parse(gql_response.headers)
            processed_cookies: List[CookiesConfig] = list()
            for gql_cookie in gql_cookies:
                cookie: CookiesConfig = CookiesConfig(
                    KEY=gql_cookie.key,
                    VALUE=gql_cookie.value,
                    EXPIRES=gql_cookie.expires,
                    PATH=gql_cookie.path,
                )

                processed_cookies.append(cookie)

            result.cookies = processed_cookies

    except Exception as error:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(error),
                default_message="Ошибка аутентификации"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def verify_email(  # type: ignore[return]
        verify_email_token: str,
) -> Optional[str]:
    try:
        await config.graphql_client.gql_query(
            query=VerifyUserEmailMutation.to_gql(),
            variable_values=VerifyUserEmailVariables(
                verify_email_token=verify_email_token,
            ).to_dict()
        )

    except Exception as error:
        return ERRORS_MAPPING.get(
            extract_error_message(
                error=str(error),
                default_message="Ошибка подтверждения email"
            ),
            DEFAULT_ERROR_MESSAGE
        )


async def get_me(
        request: Request,
) -> GetMeResponse:
    result: GetMeResponse = GetMeResponse()

    if len(request.cookies) == 0:
        result.error = "no accessToken cookie provided"
        return result

    try:
        if request.cookies:
            gql_response = await config.graphql_client.gql_query(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=request.cookies
            )

            if gql_response.result["me"] != "null":
                result.user = User(
                    id=gql_response.result["me"]["id"],
                    email=gql_response.result["me"]["email"],
                    display_name=gql_response.result["me"]["displayName"],
                )

            if "error" in gql_response.result:
                result.error = gql_response.result["error"]

    except Exception as error:
        error = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(error),
                default_message="Ошибка получения данных о профиле"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result