import pytest

pytestmark = pytest.mark.usefixtures("mock_gql_client")

from unittest.mock import AsyncMock, MagicMock

from graphql_client.dto import GQLResponse
from src.domains.toys.dependencies import (
    toys_catalog,
    toy_by_id,
    toys_tags,
    toys_categories,
)
from src.domains.toys.core.dto import (
    ToysCategoriesResponse,
    ToysTagsResponse,
    ToyByIDResponse,
    ToysCatalogResponse,
)


class TestToysCatalog:
    @pytest.mark.asyncio
    async def test_toys_catalog_success(self, mock_gql_client: AsyncMock) -> None:
        mock_toys_categories = MagicMock(spec=ToysCategoriesResponse)
        mock_toys_categories.categories = [
            {"id": 1, "name": "Мягкая игрушка"},
            {"id": 2, "name": "Деревянная игрушка"}
        ]

        mock_toys_tags = MagicMock(spec=ToysTagsResponse)
        mock_toys_tags.tags = [
            {"id": 1, "name": "Хлопок"},
            {"id": 2, "name": "Лён"}
        ]

        # Первый ответ - для основного запроса
        mock_gql_response1 = MagicMock(spec=GQLResponse)
        mock_gql_response1.result = {
            "toys": [
                {
                    "id": 1,
                    "category": {"name": "Мягкая игрушка"},
                    "name": "Медведь",
                    "description": None,
                    "price": 0,
                    "quantity": 0,
                    "createdAt": None,
                    "tags": [],
                    "attachments": []
                },
            ]
        }

        # Второй ответ - для запроса счетчика
        mock_gql_response2 = MagicMock(spec=GQLResponse)
        mock_gql_response2.result = {"toysCounter": 1}

        mock_gql_client.side_effect = [mock_gql_response1, mock_gql_response2]

        result: ToysCatalogResponse = await toys_catalog(
            page=1,
            search=None,
            max_price=None,
            min_price=None,
            quantity_floor=None,
            categories=None,
            tags=None,
            sort_order=None,
            all_toys_categories=mock_toys_categories,
            all_toys_tags=mock_toys_tags,
        )

        assert result.error is None

        assert result.categories == mock_toys_categories.categories
        assert result.tags == mock_toys_tags.tags
        assert result.toys is not None
        assert result.toys[0].name == "Медведь"
        assert {"id": 1, "name": "Мягкая игрушка"} in result.categories  # type: ignore[operator]
        assert {"id": 1, "name": "Хлопок"} in result.tags  # type: ignore[operator]

    @pytest.mark.asyncio
    async def test_toys_catalog_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.return_value = {"errors": "Ошибка загрузки каталога"}

        result: ToysCatalogResponse = await toys_catalog(
            page=1,
            search=None,
            max_price=None,
            min_price=None,
            quantity_floor=None,
            categories=None,
            tags=None,
            sort_order=None,
        )

        assert result.error == "Неизвестная ошибка"
        assert result.toys == []


class TestToyByID:
    @pytest.mark.asyncio
    async def test_toys_by_id_success(self, mock_gql_client: AsyncMock) -> None:
        mock_toys_by_id = MagicMock(spec=GQLResponse)
        mock_toys_by_id.result = {
            "toy": {
                "id": 999,
                "master": {"id": 0, "user": {"avatar": "<AVATAR>", "displayName": "<USER>"}},
                "category": {"name": "<CATEGORY>"},
                "name": "<NAME>",
                "description": "<DESCRIPTION>",
                "price": 0,
                "quantity": 0,
                "createdAt": "2023-04-01T00:00:00Z",
                "tags": [{"name": "<TAG1>"}, {"name": "<TAG2>"}, {"name": "<TAG3>"}],
                "attachments": []
            }
        }

        mock_gql_client.return_value = mock_toys_by_id

        result: ToyByIDResponse = await toy_by_id(
            toy_id=999
        )

        assert result.error is None
        assert result.toy.id == 999  # type: ignore[union-attr]

        assert result.toy.master is not None  # type: ignore[union-attr]
        assert result.toy.master.id == 0  # type: ignore[union-attr]

        assert result.toy.price == 0  # type: ignore[union-attr]
        assert result.toy.quantity == 0  # type: ignore[union-attr]

        assert result.toy.tags is not None  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_toys_by_id_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_toys_by_id = MagicMock(spec=GQLResponse)
        mock_toys_by_id.result = {
            "errors": [
                {
                    "message": "<ERROR>",
                    "path": [
                        "toy"
                    ]
                },
            ]
        }

        mock_gql_client.return_value = mock_toys_by_id

        result: ToyByIDResponse = await toy_by_id(
            toy_id=999
        )

        assert result.error is not None


class TestToysCategoriesResponse:
    @pytest.mark.asyncio
    async def test_toys_categories_success(self, mock_gql_client: AsyncMock) -> None:
        mock_toys_categories = MagicMock(spec=GQLResponse)
        mock_toys_categories.result = {
            "categories": [
                {"name": "<CATEGORY1>"},
                {"name": "<CATEGORY2>"},
                {"name": "<CATEGORY3>"},
            ]
        }

        mock_gql_client.return_value = mock_toys_categories

        result: ToysCategoriesResponse = await toys_categories()

        assert result.error is None
        assert result.categories is not None

    @pytest.mark.asyncio
    async def test_toys_categories_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": "<ERROR>"}
        )

        result: ToysCategoriesResponse = await toys_categories()

        assert result.error == "Неизвестная ошибка"
        assert result.categories is None


class TestToysTagsResponse:
    @pytest.mark.asyncio
    async def test_toys_tags_success(self, mock_gql_client: AsyncMock) -> None:
        mock_toys_tags = MagicMock(spec=GQLResponse)
        mock_toys_tags.result = {
            "tags": [
                {"name": "<TAG1>"},
                {"name": "<TAG2>"},
                {"name": "<TAG3>"},
            ]
        }

        result: ToysTagsResponse = await toys_tags()

        assert result.error is None
        assert result.tags is not None

    @pytest.mark.asyncio
    async def test_toys_tags_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": "<ERROR>"}
        )

        result: ToysTagsResponse = await toys_tags()

        assert result.error == "Неизвестная ошибка"
        assert result.tags is None
