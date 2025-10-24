from pydantic import BaseModel

from src.core.cache.constants import REDIS_ERRORS, DEFAULT_REDIS_ERROR_MESSAGE


class RedisErrorValidation(BaseModel):
    orig_error: str

    def message(self) -> str:  # type: ignore
        return REDIS_ERRORS.get(
            " ".join(arg for arg in self.orig_error.replace(".", "").split()[:2]),
            DEFAULT_REDIS_ERROR_MESSAGE
        )


class RedisConfig(BaseModel):
    host: str
    port: int
    password: str
    max_connections: int
    db: int = 0
    decode_responses: bool = False
    encoding: str = "utf-8"
