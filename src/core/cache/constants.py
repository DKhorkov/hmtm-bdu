from typing import Dict

REDIS_ERRORS: Dict[str, str] = {
    "Error 111": "Подключение к Redis не удалось, проверьте состояние сервера!",
    "Authentication required": "Аутентификация не удалась, проверьте пароль",
    "Empty parameters": "Вы не задали параметры для Redis, используйте bind()"
}

DEFAULT_REDIS_ERROR_MESSAGE: str = "Неизвестная ошибка Redis"
