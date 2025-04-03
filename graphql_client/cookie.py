import datetime
from typing import List
from multidict import CIMultiDictProxy
from dataclasses import dataclass


@dataclass
class Cookie:
    key: str
    value: str
    expires: str = datetime.datetime.strftime(datetime.datetime.now(), '%a, %d %b %Y %H:%M:%S %Z')
    path: str = "/"


class CookiesParser:

    @staticmethod
    def parse(headers: CIMultiDictProxy[str]) -> List[Cookie]:
        """
        Итоговый Парсинг заголовков ответа транспорта имеет вид (Пример):
        [
        {
        'accessToken': 'ppUm...', 'Path': '/', 'Expires': 'Thu, 27 Mar 2025 07:17:35 GMT'
        },
        {
        'refreshToken': 'ZXlK..', 'Path': '/', 'Expires': 'Thu, 03 Apr 2025 07:02:35 GMT'
        }
        ]
        """
        get_cookies: List[str] = headers.getall("Set-Cookie")

        cookies: List[Cookie] = list()
        for cookie_str in get_cookies:
            cookie_parts: List[str] = cookie_str.split(";")
            token_part: List[str] = cookie_parts[0].split("=", maxsplit=1)

            if len(token_part) != 2:
                continue

            cookie: Cookie = Cookie(*token_part)
            for part in cookie_parts[1:]:
                part = part.strip()

                if "=" in part:
                    param_key, param_value = part.split("=", 1)
                    if param_key == "Expires":
                        cookie.expires = param_value
                    elif param_key == "Path":
                        cookie.path = param_value

            cookies.append(cookie)

        return cookies
