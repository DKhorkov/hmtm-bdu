import pytest

pytestmark = pytest.mark.usefixtures("mock_gql_client")

from unittest.mock import MagicMock, AsyncMock
from multidict import CIMultiDictProxy, CIMultiDict
from fastapi.requests import Request

from graphql_client.dto import GQLResponse
from src.common.dependencies import get_me
from src.common.dto import GetMeResponse


class TestGetMeDependency:
    @pytest.mark.asyncio
    async def test_get_me_with_no_cookies(self) -> None:
        """Случай, если cookies не найдены"""
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {}

        result: GetMeResponse = await get_me(mock_request)

        assert result.error == "Пользователь не найден"

    @pytest.mark.asyncio
    async def test_get_me_success(self, mock_gql_client: AsyncMock) -> None:
        """Случай, если accessToken находится в cookies"""
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {"accessToken": "Afqg..."}

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {
            "me": {
                "id": 1,
                "displayName": "Test User",
                "email": "test@example.com",
                "emailConfirmed": True,
                "phone": None,
                "phoneConfirmed": False,
                "telegram": None,
                "telegramConfirmed": False,
                "avatar": None,
                "createdAt": "2021-09-22T01:00:00",
                "updatedAt": "2021-09-22T01:00:00",
            }
        }

        mock_gql_client.return_value = mock_response

        result: GetMeResponse = await get_me(mock_request)

        assert result.error is None
        assert result.user is not None
        assert result.user.id == 1
        assert result.user.email == "test@example.com"
        assert result.user.display_name == "Test User"

    @pytest.mark.asyncio
    async def test_get_me_with_refresh_token(self, mock_gql_client: AsyncMock) -> None:
        """Случай, если accessToken истек"""
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {"accessToken": "Expired"}

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {"error": "Token Expired"}

        refresh_response: MagicMock = MagicMock(spec=GQLResponse)
        refresh_response.result = {"refreshToken": "FFsg32g..."}
        refresh_response.headers = CIMultiDictProxy(CIMultiDict({"Set-Cookie": "accessToken=new_token"}))

        success_response: MagicMock = MagicMock(spec=GQLResponse)
        success_response.result = {
            "me": {
                "id": 2,
                "email": "refresh@example.com",
                "displayName": "Refreshed User",
                "emailConfirmed": True,
                "phone": None,
                "phoneConfirmed": False,
                "telegram": None,
                "telegramConfirmed": False,
                "avatar": None,
                "createdAt": "2021-09-22T01:00:00",
                "updatedAt": "2021-09-22T01:00:00",
            }
        }

        mock_gql_client.side_effect = [mock_response, refresh_response, success_response]

        result: GetMeResponse = await get_me(mock_request)

        assert result.error is None
        assert result.user is not None
        assert result.user.id == 2
        assert result.user.email == "refresh@example.com"
        assert result.user.display_name == "Refreshed User"
        assert any(cookie.KEY == "accessToken" for cookie in result.cookies)

    @pytest.mark.asyncio
    async def test_get_me_with_refresh_token_failure(self, mock_gql_client: AsyncMock) -> None:
        """Случай, где оба запроса завершаются ошибкой"""
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {"access_token": "Expired"}

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {"error": "Token Expired"}

        refresh_response: MagicMock = MagicMock(spec=GQLResponse)
        refresh_response.result = {"errors": [{"message": "Refresh token invalid"}]}

        mock_gql_client.side_effect = [mock_response, refresh_response]

        result: GetMeResponse = await get_me(mock_request)

        assert result.error == "Неизвестная ошибка"
        assert result.user is None
