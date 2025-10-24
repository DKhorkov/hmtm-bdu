from typing import Dict

from fastapi import Depends
from fastapi.requests import Request

from graphql_client.bff_client import BFFGQLClient
from graphql_client.mutations.common import RefreshTokensMutation
from graphql_client.queries.common import GetMeQuery
from graphql_client.dto import GQLResponse
from src.core.common.dto import GetMeResponse, RefreshTokensResponse
from src.core.exc.exceptions import UserNotFoundError, RedirectViaException
from src.core.common.parsers import ModelParser
from src.core.cookies.processors import CookieProcessor
from src.core.state import GlobalAppState


class CommonAuthBaseRepository:

    @staticmethod
    async def get_me(
            request: Request,
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client),
    ) -> GetMeResponse:
        result: GetMeResponse = GetMeResponse()

        if not request.cookies:
            return result

        try:
            current_user: GQLResponse = await gql_client.execute(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=request.cookies
            )

            if "errors" in current_user.result or current_user.error:
                raise UserNotFoundError

            result.user = ModelParser.user_from_dict(current_user.result["me"])

        except UserNotFoundError:
            refreshed_tokens: RefreshTokensResponse = await CommonAuthBaseRepository._refresh_tokens(
                cookies=request.cookies,
                gql_client=gql_client
            )

            if refreshed_tokens.error:
                return result

            result.cookies = refreshed_tokens.cookies

            actual_cookies: Dict[str, str] = {}
            for cookie in refreshed_tokens.cookies:
                actual_cookies[cookie.KEY] = cookie.VALUE

            current_user: GQLResponse = await gql_client.execute(  # type: ignore
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=actual_cookies
            )

            if "errors" in current_user.result or current_user.error:
                return result

            result.user = ModelParser.user_from_dict(current_user.result["me"])

        return result

    @staticmethod
    async def _refresh_tokens(
            gql_client: BFFGQLClient,
            cookies: Dict[str, str]
    ) -> RefreshTokensResponse:
        result: RefreshTokensResponse = RefreshTokensResponse()

        gql_refresh_tokens: GQLResponse = await gql_client.execute(
            query=RefreshTokensMutation.to_gql(),
            variable_values={},
            cookies=cookies
        )

        if gql_refresh_tokens.error is not None:
            result.error = gql_refresh_tokens.error
            return result

        if gql_refresh_tokens.headers:
            result.cookies = CookieProcessor.get_cookies_from_gql_headers(gql_refresh_tokens.headers)

        return result


class CommonAuthRedirectRepository:

    @staticmethod
    async def get_me_with_redirect_if_user(
            request: Request,
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> GetMeResponse:
        result: GetMeResponse = await CommonAuthBaseRepository.get_me(
            request=request,
            gql_client=gql_client
        )

        if result.user:
            raise RedirectViaException(url="/", value="4020", cookies=result.cookies)

        return result

    @staticmethod
    async def get_me_with_redirect_if_not_user(
            request: Request,
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> GetMeResponse:
        result: GetMeResponse = await CommonAuthBaseRepository.get_me(
            request=request,
            gql_client=gql_client
        )

        if not result.user:
            raise RedirectViaException(url="/sso/login", value="4017", cookies=result.cookies)

        return result
