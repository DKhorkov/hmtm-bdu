from typing import Dict, Optional, List
from multidict import CIMultiDictProxy


class Cookies:

    @staticmethod
    def pars(headers: Optional[CIMultiDictProxy[str]]) -> Optional[List[Dict[str, str]]]:
        if headers is None:
            return None

        get_cookies = headers.getall("Set-Cookie")

        new_cookies = []

        for cookies in get_cookies:
            cookie_parts = cookies.split(";")
            token_part = cookie_parts[0].split("=")

            if len(token_part) != 2:
                continue

            key, value = token_part
            cookie_dict = {key: value}

            for part in cookie_parts[1:]:
                part = part.strip()

                if "=" in part:
                    param_key, param_value = part.split("=", 1)
                    cookie_dict[param_key] = param_value

            new_cookies.append(cookie_dict)

        cookies = new_cookies
        return cookies
        
        # Итоговый Парсинг заголовков ответа транспорта имеет вид (Пример):
        # [
        #     {
        #         'accessToken': 'ppUm...', 'Path': '/', 'Expires': 'Thu, 27 Mar 2025 07:17:35 GMT'
        #     },
        #     {
        #         'refreshToken': 'ZXlK..', 'Path': '/', 'Expires': 'Thu, 03 Apr 2025 07:02:35 GMT'
        #     }
        # ]
