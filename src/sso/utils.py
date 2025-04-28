from typing import Dict, Any

from src.sso.datetime_parser import DatetimeParser
from src.sso.models import User


def user_from_dict(user_data: Dict[str, Any]) -> User:
    return User(
        id=user_data["id"],
        display_name=user_data["displayName"],
        email=user_data["email"],
        email_confirmed=user_data["emailConfirmed"],
        phone=user_data["phone"],
        phone_confirmed=user_data["phoneConfirmed"],
        telegram=user_data["telegram"],
        telegram_confirmed=user_data["telegramConfirmed"],
        avatar=user_data["avatar"],
        created_at=DatetimeParser.parse(user_data["createdAt"]),
        updated_at=DatetimeParser.parse(user_data["updatedAt"]),
    )
