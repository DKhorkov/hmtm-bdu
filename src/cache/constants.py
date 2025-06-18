from typing import Dict
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env"))

REDIS_ERRORS: Dict[str, str] = {
    "Error 111": "Подключение к Redis не удалось, проверьте состояние сервера!",
    "Authentication required": "Аутентификация не удалась, проверьте пароль"
}

DEFAULT_REDIS_ERROR_MESSAGE: str = "Неизвестная ошибка Redis"

# Redis environments:
DB: int = 0
DECODE_RESPONSES: bool = False
ENCODING: str = "utf-8"
MAX_CONNECTIONS: int = 10
