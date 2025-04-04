import pytest

from unittest.mock import AsyncMock, patch, MagicMock
from graphql import DocumentNode
from typing import Generator, Optional, Dict
from multidict import CIMultiDictProxy, CIMultiDict
from fastapi.requests import Request

from src.sso.dependencies import (
    process_register,
    process_login,
    verify_email,
    get_me
)
from graphql_client.client import GraphQLClient
from graphql_client.dto import GQLResponse
from src.sso.dto import LoginResponse, GetMeResponse


@pytest.fixture(scope="function")
def mock_gql_client() -> Generator[AsyncMock, None, None]:
    """Фикстура через декоратор @patch не работает из-за особенностей pytest-а"""
    with patch.object(target=GraphQLClient, attribute="gql_query", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture(scope="function")
def mock_success_login_response() -> Generator[MagicMock, None, None]:
    headers: CIMultiDict = CIMultiDict()
    headers.add("Set-Cookie", "accessToken=3FG2gs...; Path=...; Expires=...")
    headers_proxy = CIMultiDictProxy(headers)

    mock: MagicMock = MagicMock(spec=GQLResponse)
    mock.headers = headers_proxy
    mock.result = {"loginUser": True}

    yield mock


@pytest.fixture(scope="function")
def mock_failed_login_response() -> Generator[MagicMock, None, None]:
    mock: MagicMock = MagicMock(spec=GQLResponse)
    mock.headers = None
    mock.result = False

    yield mock


class TestProcessRegisterDependency:
    @pytest.mark.asyncio
    async def test_process_register_success(self, mock_gql_client: AsyncMock) -> None:
        """Мокаем возвращаемое значение через return_value"""
        mock_gql_client.return_value = {"registerUser": "123"}

        result: Optional[str] = await process_register(
            email="test@example.com",
            password="password123",
            display_name="Test User"
        )

        """Проверяем, что метод process_register отработала без ошибок"""
        assert result is None

        """Проверяем, что метод был вызван один раз"""
        mock_gql_client.assert_called_once()

        """Получаем kwargs-аргументы из метода"""
        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs

        """Сверяем, что запрос(query) является типом DocumentNode"""
        assert isinstance(call_kwargs["query"], DocumentNode)

        """Сверяем, что variables соответствуют возврату словаря с функции to_dict()"""
        assert call_kwargs["variable_values"] == {
            "input": {
                "displayName": "Test User",
                "email": "test@example.com",
                "password": "password123"
            }
        }

    @pytest.mark.asyncio
    async def test_process_register_failure(self, mock_gql_client: AsyncMock) -> None:
        """Мокаем возвращаемую ошибку через side_effect"""
        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = Internal desc = password does not meet the requirements"}
        )

        result: Optional[str] = await process_register(
            email="test@example.com",
            password="",
            display_name="Test_User"
        )

        """Сверяем, что результат функции выдает нужную ошибку по переданному ключу"""
        assert result == "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол."

        mock_gql_client.assert_called_once()


class TestProcessLoginDependency:
    @pytest.mark.asyncio
    async def test_login_success(self, mock_gql_client: AsyncMock, mock_success_login_response: MagicMock) -> None:
        mock_gql_client.return_value = mock_success_login_response

        result: LoginResponse = await process_login(
            email="test@example.com",
            password="password123",
        )

        mock_gql_client.assert_called_once()

        assert result.error is None
        assert result.result is True
        assert result.headers == mock_success_login_response.headers

        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs
        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "email": "test@example.com",
                "password": "password123"
            }
        }

    @pytest.mark.asyncio
    async def test_login_failure(self, mock_gql_client: AsyncMock, mock_failed_login_response: MagicMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = NotFound desc = user not found"}
        )

        result: LoginResponse = await process_login(
            email="test@example.com",
            password="password123",
        )

        mock_gql_client.assert_called_once()

        assert result.headers is None
        assert result.result is False
        assert result.cookies == []
        assert result.error == "Пользователь не найден"


class TestVerifyEmailDependency:
    @pytest.mark.asyncio
    async def test_verify_email_success(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.return_value = {"verifyEmail": True}

        result: Optional[str] = await verify_email(
            verify_email_token="Test-token-1",
        )

        assert result is None

        mock_gql_client.assert_called_once()
        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs

        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "verifyEmailToken": "Test-token-1",
            }
        }

    @pytest.mark.asyncio
    async def test_verify_email_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": "Ошибка подтверждения email"}
        )

        result: Optional[str] = await verify_email(
            verify_email_token="Test-token-1",
        )

        assert result == "Ошибка подтверждения email"

        mock_gql_client.assert_called_once()


class TestGetMeDependency:
    @pytest.mark.asyncio
    async def test_get_me_with_no_cookies(self) -> None:
        """Случай, если cookies не найдены"""
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {}

        result: GetMeResponse = await get_me(mock_request)

        assert result.error == "AccessToken не найден"

    @pytest.mark.asyncio
    async def test_get_me_success(self, mock_gql_client: AsyncMock) -> None:
        """Случай, если accessToken находится в cookies"""
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {"accessToken": "Afqg..."}

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {
            "me": {
                "id": 1,
                "email": "test@example.com",
                "displayName": "Test User",
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
                "displayName": "Refreshed User"
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

        assert result.error == "Refresh token invalid"
        assert result.user is None
