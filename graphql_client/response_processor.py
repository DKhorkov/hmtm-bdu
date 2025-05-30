from typing import List

from graphql_client.dto import GQLResponse
from src.common.cookies import CookiesConfig
from graphql_client.cookie import Cookie as GQLCookie, CookiesParser


class ResponseProcessor:
    def __init__(self, gql_response: GQLResponse):
        self.__response = gql_response

    def get_cookies(self) -> List[CookiesConfig]:
        gql_cookies: List[GQLCookie] = CookiesParser.parse(self.__response.headers)  # type: ignore[arg-type]
        processed_cookies: List[CookiesConfig] = list()
        for gql_cookie in gql_cookies:
            cookie: CookiesConfig = CookiesConfig(
                KEY=gql_cookie.key,
                VALUE=gql_cookie.value,
                EXPIRES=gql_cookie.expires,
                PATH=gql_cookie.path,
            )

            processed_cookies.append(cookie)

        return processed_cookies
