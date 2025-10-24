from typing import Set

DEFAULT_ERROR_CODE: str = "5001"
UNKNOWN_ERROR: str = "Неизвестная ошибка, попробуйте позже или обратитесь в поддержку!"
ERROR_OPERATION_KEY: str = "x-error-code"
SUCCESS_OPERATION_KEY: str = "x-success-code"

SESSIONS_COOKIE_KEYS: Set[str] = {"accessToken", "refreshToken"}
