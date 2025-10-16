from datetime import datetime
from typing import Any, Dict

from src.core.common.dto import User
from src.domains.profile.core.schemas import Master
from src.domains.toys.core.models import (
    ToyForCatalog,
    ToyTag,
    ToyCategory,
    ToyAttachment,
    ToyForCard,
    MasterForToyCard,
    UserForToyCard
)


class DatetimeParser:

    @staticmethod
    def parse_iso_format(iso_date: str) -> str:
        try:
            return datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d.%m.%Y")

        except Exception:  # noqa
            return "Ошибка загрузки формата даты"


class ModelParser:

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
            created_at=DatetimeParser.parse_iso_format(user["createdAt"]),
            updated_at=DatetimeParser.parse_iso_format(user["updatedAt"]),
        )

    @staticmethod
    def toy_for_catalog_from_dict(toy: Dict[str, Any]) -> ToyForCatalog:
        return ToyForCatalog(
            id=toy["id"],
            category=ToyCategory(name=toy["category"]["name"]),
            name=toy["name"],
            description=toy["description"],
            price=round(toy["price"], 2),
            quantity=toy["quantity"],
            created_at=DatetimeParser.parse_iso_format(toy["createdAt"]),
            tags=[ToyTag(name=tag["name"]) for tag in toy["tags"]],
            attachments=[
                ToyAttachment(link=attachments["link"]) for attachments in toy["attachments"]
            ]
        )

    @staticmethod
    def toy_for_card_from_dict(toy: Dict[str, Any]) -> ToyForCard:
        return ToyForCard(
            id=toy["id"],
            master=MasterForToyCard(
                id=toy["master"]["id"],
                user=UserForToyCard(
                    avatar=toy["master"]["user"]["avatar"],
                    display_name=toy["master"]["user"]["displayName"],
                )
            ),
            category=ToyCategory(name=toy["category"]["name"]),
            name=toy["name"],
            description=toy["description"],
            price=round(toy["price"], 2),
            quantity=toy["quantity"],
            created_at=DatetimeParser.parse_iso_format(toy["createdAt"]),
            tags=[ToyTag(name=tag["name"]) for tag in toy["tags"]],
            attachments=[ToyAttachment(link=attachments["link"]) for attachments in toy["attachments"]],
        )

    @staticmethod
    def master_from_dict(master: Dict[str, Any]) -> Master:
        return Master(
            id=master["id"],
            info=master["info"],
            created_at=DatetimeParser.parse_iso_format(master["createdAt"]),
            updated_at=DatetimeParser.parse_iso_format(master["updatedAt"])
        )
