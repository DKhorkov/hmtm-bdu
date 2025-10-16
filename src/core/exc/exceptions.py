from typing import Optional, List

from src.core.cookies.schemas import CookiesConfig


class HmtmBduException(Exception):
    pass


class UserNotFoundError(HmtmBduException):
    pass


class RedirectViaException(HmtmBduException):
    def __init__(self, value: str, url: str = "/", cookies: Optional[List[CookiesConfig]] = None) -> None:
        self.url = url
        self.value = value
        self.cookies = cookies
