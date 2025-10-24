from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Cookie(BaseModel):
    KEY: str
    VALUE: str
    EXPIRES: str = datetime.strftime(datetime.now(), '%a, %d %b %Y %H:%M:%S %Z')
    PATH: str = "/"


class CookiesConfig(BaseModel):
    KEY: str
    VALUE: str
    EXPIRES: str
    SECURE_COOKIES: bool = False
    HTTP_ONLY: bool = False
    SAME_SITE: Literal["lax", "strict", "none"] = "lax"
    PATH: str = "/"
