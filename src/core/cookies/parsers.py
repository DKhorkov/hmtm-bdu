from typing import List

from src.core.cookies.schemas import Cookie


class CookiesParser:

    @staticmethod
    def parse(response_cookies: List[str]) -> List[Cookie]:
        """
        Парсит cookie определенного вида от ответа graphql

        Args:
            response_cookies: List[str] -> :
            [
                'accessToken=eyJhbGciOiJIUzI1N.eyJleHAiOjE3.YqIu6YmKGf-kNopVkuLEMk;
                 Path=/; Expires=Tue, 25 Mar 2025 08:22:57 GMT',

                'refreshToken=ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFh;
                Path=/; Expires=Tue, 01 Apr 2025 08:07:57 GMT'
            ]
        """
        cookies: List[Cookie] = []
        for cookie_str_data in response_cookies:
            cookie: List[str] = cookie_str_data.split(";")
            token_attrs: List[str] = cookie[0].split("=", maxsplit=1)

            cookies.append(Cookie(
                KEY=token_attrs[0],
                VALUE=token_attrs[1],
                PATH=cookie[1].split("=", maxsplit=1)[1],
                EXPIRES=cookie[2].split("=", maxsplit=1)[1]
            ))

        return cookies
