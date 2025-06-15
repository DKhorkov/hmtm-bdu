from typing import Dict

REDIS_ERRORS: Dict[str, str] = {
    "Error 111": "Подключение к Redis не удалось, проверьте состояние сервера!",
    "Authentication required": "Аутентификация не удалась, проверьте пароль"
}

DEFAULT_REDIS_ERROR_MESSAGE: str = "Неизвестная ошибка Redis"
