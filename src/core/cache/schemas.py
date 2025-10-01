from pydantic import BaseModel, field_validator

from src.core.cache.constants import REDIS_ERRORS, DEFAULT_REDIS_ERROR_MESSAGE


class RedisErrorValidationModel(BaseModel):
    error: str

    @field_validator("error", mode="before")  # noqa
    @classmethod
    def validate(cls, value: str) -> str:  # type: ignore
        return REDIS_ERRORS.get(
            " ".join(arg for arg in value.replace(".", "").split()[:2]),
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
