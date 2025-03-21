import pytest

from unittest.mock import AsyncMock, patch
from graphql import DocumentNode
from typing import Generator

from src.sso.dependencies import (
    process_register,
    process_login,
    verify_email
)
from graphql_client.client import GraphQLClient


@pytest.fixture
def mock_gql_client() -> Generator[AsyncMock, None, None]:
    """Фикстура через декоратор @patch не работает из-за особенностей pytest-а"""
    with patch.object(target=GraphQLClient, attribute="gql_query", new_callable=AsyncMock) as mock:
        yield mock


class TestProcessRegisterDependency:

    @pytest.mark.asyncio
    async def test_process_register_success(self, mock_gql_client: AsyncMock) -> None:
        """МОКаем возвращаемое значение через return_value"""
        mock_gql_client.return_value = {"registerUser": "123"}

        result = await process_register(
            email="test@example.com",
            password="password123",
            display_name="Test User"
        )

        """Проверяем, что метод process_register отработала без ошибок"""
        assert result is None

        """Проверяем, что метод был вызван один раз"""
        mock_gql_client.assert_called_once()

        """Получаем kwargs-аргументы из метода"""
        call_kwargs = mock_gql_client.call_args.kwargs

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
    async def test_process_register_failure(self, mock_gql_client: AsyncMock):
        """МОКаем возвращаемую ошибку через side_effect"""
        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = Internal desc = password does not meet the requirements"}
        )

        result = await process_register(
            email="test@example.com",
            password="",
            display_name="Test_User"
        )

        """Сверяем, что результат функции выдает нужную ошибку по переданному ключу"""
        assert result == "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол."

        mock_gql_client.assert_called_once()


class TestProcessLoginDependency:

    @pytest.mark.asyncio
    async def test_login_success(self, mock_gql_client: AsyncMock):
        mock_gql_client.return_value = {"loginUser": True}

        result = await process_login(
            email="test@example.com",
            password="Valid_password"
        )

        assert result is None

        mock_gql_client.assert_called_once()
        call_kwargs = mock_gql_client.call_args.kwargs

        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "email": "test@example.com",
                "password": "Valid_password"
            }
        }

    @pytest.mark.asyncio
    async def test_login_failure(self, mock_gql_client: AsyncMock):
        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = Internal desc = user with provided email already exists"}
        )

        result = await process_login(
            email="unvalid_email@abc.com",
            password="Valid_password"
        )

        assert result == "Пользователь с таким email уже существует"

        mock_gql_client.assert_called_once()


class TestVerifyEmailDependency:

    @pytest.mark.asyncio
    async def test_verify_email_success(self, mock_gql_client: AsyncMock):
        mock_gql_client.return_value = {"verifyEmail": True}

        result = await verify_email(
            verify_email_token="Test-token-1",
        )

        assert result is None

        mock_gql_client.assert_called_once()
        call_kwargs = mock_gql_client.call_args.kwargs

        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "verifyEmailToken": "Test-token-1",
            }
        }

    @pytest.mark.asyncio
    async def test_verify_email_failure(self, mock_gql_client):
        mock_gql_client.side_effect = Exception(
            {"message": "Ошибка подтверждения email"}
        )

        result = await verify_email(
            verify_email_token="Test-token-1",
        )

        assert result == "Ошибка подтверждения email"

        mock_gql_client.assert_called_once()
