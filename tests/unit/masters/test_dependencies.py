import pytest

from graphql_client.dto import GQLResponse
from src.domains.masters.core.dto import MasterForCatalog

pytestmark = pytest.mark.usefixtures("mock_gql_client")

from unittest.mock import AsyncMock, MagicMock

from src.domains.masters.dependencies import masters_catalog
from src.domains.masters.core.dto import MastersCatalogResponse


class TestMastersCatalog:
    @pytest.mark.asyncio
    async def test_masters_catalog_success(self, mock_gql_client: AsyncMock) -> None:
        mock_masters_catalog = MagicMock(spec=GQLResponse)
        mock_masters_catalog.result = {
            "masters": [
                {
                    "id": 1,
                    "info": "Мастер",
                    "createdAt": "2025-07-25T09:57:27.35471Z"
                },
            ]
        }

        mock_masters_counter = MagicMock(spec=GQLResponse)
        mock_masters_counter.result = {"mastersCounter": 1}

        mock_gql_client.side_effect = [mock_masters_catalog, mock_masters_counter]

        result: MastersCatalogResponse = await masters_catalog(
            page=1
        )

        assert result.error is None
        assert result.current_page == 1
        assert result.total_pages == 1
        assert result.masters == [
            MasterForCatalog(
                id=1,
                info="Мастер",
                created_at="25.07.2025"
            )
        ]

    @pytest.mark.asyncio
    async def test_masters_catalog_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.return_value = {"errors": "Ошибка загрузки каталога"}

        result: MastersCatalogResponse = await masters_catalog(
            page=1
        )

        assert result.error == "Неизвестная ошибка"
        assert not result.masters
