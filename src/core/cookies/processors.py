from gzip import compress as gzip_compress, decompress as gzip_decompress
from json import dumps as json_dumps, loads as json_loads
from base64 import b64encode as base64_encode, b64decode as base64_decode
from typing import List, Optional, Any, Dict
from multidict import CIMultiDictProxy

from fastapi import Response, Request

from src.core.common.constants import SESSIONS_COOKIE_KEYS
from src.core.cookies.parsers import CookiesParser
from src.core.cookies.schemas import CookiesConfig


class CookieCompressor:

    @staticmethod
    def compress(data: Any) -> Optional[str]:
        """Сжатие любого типа данных через JSON"""
        try:
            compressed_data: bytes = gzip_compress(json_dumps(data, ensure_ascii=False).encode())
            return base64_encode(compressed_data).decode("ascii")

        except Exception:  # noqa
            return None

    @staticmethod
    def decompress(compressed_data: Optional[str]) -> Optional[Any]:
        if not compressed_data:
            return None

        try:
            decompressed_data: str = gzip_decompress(base64_decode(compressed_data)).decode()
            return json_loads(decompressed_data)

        except Exception:  # noqa
            return None


class CookieProcessor:

    @staticmethod
    def set_cookie(response: Response, cookie_config: CookiesConfig) -> None:
        response.set_cookie(
            key=cookie_config.KEY,
            value=cookie_config.VALUE,
            secure=cookie_config.SECURE_COOKIES,
            expires=cookie_config.EXPIRES,
            httponly=cookie_config.HTTP_ONLY,
            samesite=cookie_config.SAME_SITE,
            path=cookie_config.PATH
        )

    @staticmethod
    def delete_cookie(response: Response, cookie_config: CookiesConfig) -> None:
        response.delete_cookie(
            key=cookie_config.KEY,
            secure=cookie_config.SECURE_COOKIES,
            httponly=cookie_config.HTTP_ONLY,
            samesite=cookie_config.SAME_SITE
        )

    @staticmethod
    def get_cookies_from_gql_headers(response_headers: Optional[CIMultiDictProxy[str]]) -> List[CookiesConfig]:
        if not response_headers:
            return []

        return [
            CookiesConfig(**gql_cookie.model_dump())
            for gql_cookie in CookiesParser.parse(response_headers.getall("Set-Cookie"))
        ]

    @staticmethod
    def delete_temp_cookies(request: Request, response: Response) -> None:
        for cookie in request.cookies:
            if cookie not in SESSIONS_COOKIE_KEYS:
                response.delete_cookie(key=cookie)

    @staticmethod
    def get_actual_dict_cookies(request: Request, cookies: Optional[List[CookiesConfig]]) -> Dict[str, str]:
        actual_cookies: Dict[str, str] = request.cookies

        if cookies:
            for cookie in cookies:
                actual_cookies[cookie.KEY] = cookie.VALUE

        return actual_cookies
