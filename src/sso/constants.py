from typing import Dict

ERRORS_MAPPING: Dict[str, str] = {
    'rpc error: code = FailedPrecondition desc = password does not meet the requirements':
        "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол.",

    'rpc error: code = FailedPrecondition desc = email does not meet the requirements':
        "Некорректный email",

    "Ошибка регистрации": "Ошибка регистрации",

    'rpc error: code = FailedPrecondition desc = display name not meet the requirements':
        "Имя пользователя не может быть короче 4-х символов",

    'rpc error: code = AlreadyExists desc = user with provided email already exists':
        "Пользователь с таким email уже существует",

    "Ошибка аутентификации": "Ошибка аутентификации",

    "Ошибка подтверждения email": "Ошибка подтверждения email",

    'rpc error: code = Unauthenticated desc = wrong password': "Неверный email или пароль",

    'rpc error: code = NotFound desc = user not found': "Пользователь не найден",

    'permission denied: User with this email has not confirmed it':
        """
            Необходимо подтвердить email, пожалуйста проверьте свой почтовый ящик.
            Если письмо не пришло, нажмите: Отправить письмо подтверждения повторно
        """,

    "rpc error: code = FailedPrecondition desc = provided email has been already confirmed":
        "Ваша почта уже подтверждена",

    "rpc error: code = FailedPrecondition desc = New password can not be equal to old password":
        "Новый пароль идентичен старому",

}

FORGET_PASSWORD_TOKEN_NAME = "forget_password_token"
