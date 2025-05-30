from typing import Literal
from fastapi import Response
from dataclasses import dataclass


@dataclass
class CookiesConfig:
    KEY: str
    VALUE: str
    EXPIRES: str
    SECURE_COOKIES: bool = False
    HTTP_ONLY: bool = False
    SAME_SITE: Literal["lax", "strict", "none"] = "lax"
    PATH: str = "/"


def set_cookie(response: Response, cookie_config: CookiesConfig) -> Response:
    response.set_cookie(
        key=cookie_config.KEY,
        value=cookie_config.VALUE,
        secure=cookie_config.SECURE_COOKIES,
        expires=cookie_config.EXPIRES,
        httponly=cookie_config.HTTP_ONLY,
        samesite=cookie_config.SAME_SITE,
        path=cookie_config.PATH
    )

    return response


def delete_cookie(response: Response, cookie_config: CookiesConfig) -> Response:
    response.delete_cookie(
        key=cookie_config.KEY,
        secure=cookie_config.SECURE_COOKIES,
        httponly=cookie_config.HTTP_ONLY,
        samesite=cookie_config.SAME_SITE
    )

    return response
