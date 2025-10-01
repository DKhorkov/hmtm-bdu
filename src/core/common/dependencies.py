from typing import Optional, List, Dict

from fastapi.requests import Request

from graphql_client import (
    extract_error_message,
    ResponseProcessor as GQLResponseProcessor
)
from graphql_client.mutations.common import RefreshTokensMutation
from graphql_client.queries.common import GetMeQuery
from graphql_client.dto import GQLResponse
from src.core.config import config
from src.core.common.constants import DEFAULT_ERROR_MESSAGE, COMMON_ERRORS_MAPPER
from src.core.common.cookies import CookiesConfig
from src.core.common.dto import GetMeResponse, RefreshTokensResponse
from src.core.common.parsers import Parse


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
            gql_response: GQLResponse = await config.graphql_client.execute(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=actual_cookies
            )
            if "errors" in gql_response.result:
                raise Exception

            result.user = Parse.user_from_dict(gql_response.result["me"])

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

            gql_get_me: GQLResponse = await config.graphql_client.execute(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=actual_cookies
            )

            if "errors" in gql_get_me.result:
                raise Exception(gql_get_me.result["errors"][0]["message"])

            result.user = Parse.user_from_dict(gql_get_me.result["me"])

        except Exception as err:
            error = COMMON_ERRORS_MAPPER.get(
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
        gql_refresh_tokens: GQLResponse = await config.graphql_client.execute(
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
        error: str = COMMON_ERRORS_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка обновления токенов"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result
