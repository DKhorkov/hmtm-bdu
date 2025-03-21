from typing import Dict

ERRORS_MAPPING: Dict[str, str] = {
    'rpc error: code = Internal desc = password does not meet the requirements':
        "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол.",

    'rpc error: code = Internal desc = email does not meet the requirements':
        "Некорректный email",

    "Ошибка регистрации": "Ошибка регистрации",

    'rpc error: code = Internal desc = display name not meet the requirements':
        "Имя пользователя не может быть короче 4-х символов",

    'rpc error: code = Internal desc = user with provided email already exists':
        "Пользователь с таким email уже существует",

    "Ошибка аутентификации": "Ошибка аутентификации",

    "Ошибка подтверждения email": "Ошибка подтверждения email",

    'rpc error: code = Internal desc = wrong password': "Неверный email или пароль",

    'rpc error: code = Internal desc = user not found': "Пользователь не найден",

}
