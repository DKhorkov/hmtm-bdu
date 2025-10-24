import pytest

pytestmark = pytest.mark.usefixtures(
    "mock_gql_client",
    "mock_success_login_response",
    "mock_failed_login_response",
    "mock_gql_user_response_by_id",
    "mock_gql_master_response",
    "mock_gql_user_response_by_email"
)

from unittest.mock import AsyncMock, MagicMock
from fastapi.requests import Request

from graphql import DocumentNode
from typing import Dict

from src.domains.sso.core.constants import FORGET_PASSWORD_TOKEN_NAME
from src.domains.sso.core.dependencies import (
    process_register,
    process_login,
    verify_email,
    send_verify_email_message,
    send_forget_password_message,
    change_forget_password,
    get_user_info,
)
from graphql_client.dto import GQLResponse
from src.domains.sso.core.dependencies import (
    LoginResponse,
    RegisterResponse,
    VerifyEmailResponse,
    SendVerifyEmailMessageResponse,
    SendForgetPasswordMessageResponse,
    ChangeForgetPasswordResponse,
    GetFullUserInfoResponse,
)


class TestProcessRegisterDependency:
    @pytest.mark.asyncio
    async def test_process_register_success(self, mock_gql_client: AsyncMock) -> None:
        """Мокаем возвращаемы dto-object из gql-клиента"""
        mock_gql_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_gql_response.result = {"registerUser": True}
        mock_gql_response.headers = {}

        """Мокаем возвращаемое значение через return_value"""
        mock_gql_client.return_value = mock_gql_response

        result: RegisterResponse = await process_register(
            email="test@example.com",
            password="password123",
            display_name="Test User"
        )

        """Проверяем, что метод был вызван один раз"""
        mock_gql_client.assert_called_once()

        """Проверяем, что метод process_register отработала без ошибок"""
        assert result.error is None
        assert result.result is True
        assert result.headers == mock_gql_response.headers

        """Получаем kwargs-аргументы из метода"""
        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs

        """Сверяем, что запрос(query) является типом DocumentNode"""
        assert isinstance(call_kwargs["query"], DocumentNode)

        """Сверяем, что variables соответствуют возврату словаря с функции to_dict()"""
        assert call_kwargs["params"] == {
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
            {"message": "rpc error: code = FailedPrecondition desc = password does not meet the requirements"}
        )

        result: RegisterResponse = await process_register(
            email="test@example.com",
            password="",
            display_name="Test_User"
        )

        """Сверяем, что результат функции выдает нужную ошибку по переданному ключу"""
        assert result.error == "Пароль не соответствует требованиям: 8+ символов, A-Z, a-z, 0-9, спецсимвол."

        """Сверяем остальные параметры"""
        assert result.result is False
        assert result.cookies == []
        assert result.headers is None

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
        assert call_kwargs["params"] == {
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
        mock_gql_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_gql_response.result = {"verifyEmail": True}
        mock_gql_response.headers = {"Cookie": "Sfqgreg..."}  # Headers - обязателен

        mock_gql_client.return_value = mock_gql_response

        result: VerifyEmailResponse = await verify_email(
            verify_email_token="Test-token-1",
        )

        mock_gql_client.assert_called_once()

        assert result.error is None
        assert result.result is True
        assert result.headers == mock_gql_response.headers

        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs

        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["params"] == {
            "input": {
                "verifyEmailToken": "Test-token-1",
            }
        }

    @pytest.mark.asyncio
    async def test_verify_email_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": "Ошибка подтверждения email"}
        )

        result: VerifyEmailResponse = await verify_email(
            verify_email_token="Test-token-1",
        )

        assert result.error == "Ошибка подтверждения email"
        assert result.result is False
        assert result.cookies == []
        assert result.headers is None

        mock_gql_client.assert_called_once()


class TestSendVerifyEmailMessage:
    @pytest.mark.asyncio
    async def test_send_verify_email_success(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_gql_response.result = {"sendVerifyMessage": True}
        mock_gql_response.headers = {"Location": "https://example.com"}

        mock_gql_client.return_value = mock_gql_response

        result: SendVerifyEmailMessageResponse = await send_verify_email_message(
            email="test@example.com",
        )

        mock_gql_client.assert_called_once()

        assert result.error is None
        assert result.result is True
        assert result.headers == mock_gql_response.headers

    @pytest.mark.asyncio
    async def test_send_verify_email_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": 'rpc error: code = FailedPrecondition desc = provided email has been already confirmed'}
        )

        result: SendVerifyEmailMessageResponse = await send_verify_email_message(
            email="test@example.com",
        )

        mock_gql_client.assert_called_once()

        assert result.error == "Ваша почта уже подтверждена"
        assert result.result is False


class TestSendForgetPasswordMessage:
    @pytest.mark.asyncio
    async def test_send_forget_password_success(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_gql_response.result = {"sendForgetPasswordMessage": True}
        mock_gql_response.headers = {"Location": "https://example.com"}

        mock_gql_client.return_value = mock_gql_response

        result: SendForgetPasswordMessageResponse = await send_forget_password_message(
            email="test@example.com",
        )

        mock_gql_client.assert_called_once()

        assert result.error is None
        assert result.result is True
        assert result.headers == mock_gql_response.headers

    @pytest.mark.asyncio
    async def test_send_forget_password_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": 'rpc error: code = NotFound desc = user not found'}
        )

        result: SendForgetPasswordMessageResponse = await send_forget_password_message(
            email="test@example.com",
        )

        mock_gql_client.assert_called_once()

        assert result.error == "Пользователь не найден"
        assert result.result is False


class TestChangeForgetPassword:
    @pytest.mark.asyncio
    async def test_change_forget_password_success(self, mock_gql_client: AsyncMock) -> None:
        mock_gql_response = MagicMock(spec=GQLResponse)
        mock_gql_response.result = {"changeForgetPassword": True}
        mock_gql_response.headers = {"Location": "https://example.com"}  # Обязательно для корректного теста

        mock_request = MagicMock(spec=Request)
        mock_request.cookies = {FORGET_PASSWORD_TOKEN_NAME: "valid_token"}

        mock_gql_client.return_value = mock_gql_response

        result: ChangeForgetPasswordResponse = await change_forget_password(
            request=mock_request,
            new_password="<PASSWORD>"
        )

        mock_gql_client.assert_called_once()

        assert result.error is None
        assert result.result is True
        assert result.headers == mock_gql_response.headers

    @pytest.mark.asyncio
    async def test_change_forget_password_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_request = MagicMock(spec=Request)
        mock_request.cookies = {FORGET_PASSWORD_TOKEN_NAME: "valid_token"}

        mock_gql_client.side_effect = Exception(
            {"message": 'rpc error: code = NotFound desc = user not found'}
        )

        result: ChangeForgetPasswordResponse = await change_forget_password(
            request=mock_request,
            new_password="<PASSWORD>"
        )

        assert result.result is False
        assert result.error == "Пользователь не найден"


class TestGetUserInfo:
    @pytest.mark.asyncio
    async def test_get_user_and_master_info_success_by_id(
            self,
            mock_gql_client: AsyncMock,
            mock_gql_user_response_by_id: MagicMock,
            mock_gql_master_response: MagicMock
    ) -> None:
        mock_gql_client.side_effect = [mock_gql_user_response_by_id, mock_gql_master_response]

        result: GetFullUserInfoResponse = await get_user_info(
            query_params="777"
        )

        assert result.user is not None
        assert result.master is not None
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_get_user_and_master_info_success_by_email(
            self,
            mock_gql_client: AsyncMock,
            mock_gql_user_response_by_email: MagicMock,
            mock_gql_master_response: MagicMock
    ) -> None:
        mock_gql_client.side_effect = [mock_gql_user_response_by_email, mock_gql_master_response]

        result: GetFullUserInfoResponse = await get_user_info(
            query_params="test@example.com"
        )

        assert result.user is not None
        assert result.master is not None
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_get_user_with_no_master_success_by_id(
            self,
            mock_gql_client: AsyncMock,
            mock_gql_user_response_by_id: MagicMock,
    ) -> None:
        mock_empty_master_response = MagicMock(spec=GQLResponse)
        mock_empty_master_response.result = {
            "errors": [
                {"message": "Мастер не найден"}
            ]
        }

        mock_gql_client.side_effect = [mock_gql_user_response_by_id, mock_empty_master_response]

        result: GetFullUserInfoResponse = await get_user_info(
            query_params="777"
        )

        assert result.user is not None
        assert result.master is None
        assert result.errors == ["Мастер не найден"]

    @pytest.mark.asyncio
    async def test_get_user_info_failure_by_id(self, mock_gql_client: AsyncMock) -> None:
        mock_response = MagicMock(spec=GQLResponse)
        mock_response.return_value = {
            "errors": [
                {
                    "message": "rpc error: code = NotFound desc = user not found",
                }
            ]
        }

        mock_gql_client.return_value = mock_response

        result: GetFullUserInfoResponse = await get_user_info(
            query_params="777"
        )

        mock_gql_client.assert_called_once()

        assert result.user is None
        assert result.master is None
        assert result.errors == ["Неизвестная ошибка"]
