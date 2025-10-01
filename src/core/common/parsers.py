from datetime import datetime
from typing import Any, Dict

from src.core.common.dto import User


class Parse:

    @staticmethod
    def datetime(iso_date: str) -> str:
        try:
            return datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d.%m.%Y")

        except Exception:
            return "Ошибка загрузки формата даты"

    @staticmethod
    def user_from_dict(user: Dict[str, Any]) -> User:
        return User(
            id=user["id"],
            display_name=user["displayName"],
            email=user["email"],
            email_confirmed=user["emailConfirmed"],
            phone=user["phone"],
            phone_confirmed=user["phoneConfirmed"],
            telegram=user["telegram"],
            telegram_confirmed=user["telegramConfirmed"],
            avatar=user["avatar"],
            created_at=Parse.datetime(user["createdAt"]),
            updated_at=Parse.datetime(user["updatedAt"]),
        )
