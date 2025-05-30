from typing import Optional, List, Dict

from fastapi.requests import Request
from graphql_client import (
    GetMeQuery,
    extract_error_message,
    RefreshTokensMutation,
    ResponseProcessor as GQLResponseProcessor
)
from graphql_client.dto import GQLResponse
from src.common.config import config
from src.common.constants import DEFAULT_ERROR_MESSAGE, ERRORS_MAPPING
from src.common.cookies import CookiesConfig
from src.common.dto import GetMeResponse, RefreshTokensResponse
from src.common.utils import user_from_dict


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
                raise Exception(refreshed_tokens.error)

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
                raise Exception(gql_get_me.result["errors"][0]["message"])

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
            raise Exception(gql_refresh_tokens.result["errors"][0])

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
