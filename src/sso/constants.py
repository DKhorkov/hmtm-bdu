from typing import Dict

ERRORS_MAPPING: Dict[str, str] = {
    "Пользователь не авторизован": "Пользователь не авторизован",

    'rpc error: code = FailedPrecondition desc = password does not meet the requirements':
        "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол.",

    "rpc error: code = Internal desc = password does not meet the requirements":
        "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол.",

    "rpc error: code = Internal desc = wrong password":
        "Вы ввели неправильный текущий пароль",

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

    "invalid file extension=.webp":
        "Файл с расширением webp не поддерживается к загрузке",

    "accessToken cookie not found": "Токен авторизации не был найден, пожалуйста, обновите страницу",

    "rpc error: code = Unauthenticated desc = JWT token is invalid or has expired%!(EXTRA string=)":
        "Некорректный или просроченный токен",

    "rpc error: code = FailedPrecondition desc = telegram not meet the requirements":
        "Некорректное имя пользователя для telegram",

    "rpc error: code = FailedPrecondition desc = phone not meet the requirements":
        "Некорректный номер телефона",

    "rpc error: code = NotFound desc = master not found":
        "Пользователь не является мастером",

    'rpc error: code = AlreadyExists desc = master already exists':
        "Мастер уже зарегестрирован"
}

REQUEST_ENVIRONMENTS_MAPPING: Dict[str, str] = {
    "user_not_found": "Пользователь не найден!",

    "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол.":
        "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол.",

    "Имя пользователя не может быть короче 4-х символов":
        "Имя пользователя не может быть короче 4-х символов!",

    "Некорректное имя пользователя для telegram":
        "Некорректное имя пользователя для telegram!",

    "Некорректный номер телефона":
        "Некорректный номер телефона!",

    "Вы успешно поменяли данные о себе":
        "Вы успешно поменяли данные о себе",

    "Вы успешно поменяли данные о мастере":
        "Вы успешно поменяли данные о мастере",

    "Вы успешно стали мастером!":
        "Вы успешно стали мастером!",

    "Вы успешно поменяли пароль!":
        "Вы успешно поменяли пароль!",

    "Вы уже зарегистрированы!":
        "Вы уже зарегистрированы!",

    "У вас активная сессия!":
        "У вас активная сессия!",

    "Ваша почта уже подтверждена!":
        "Ваша почта уже подтверждена!",

    "Для смены забытого пароля вам необходима форма в профиле":
        "Для смены забытого пароля вам необходима форма в профиле",

    "Письмо о смене пароля отправлено на почту, указанную при регистрации!":
        "Письмо о смене пароля отправлено на почту, указанную при регистрации!",

    "Пользователь не найден":
        "Пользователь не найден",
}

FORGET_PASSWORD_TOKEN_NAME: str = "forget_password_token"
