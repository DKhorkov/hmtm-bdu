import pytest

from unittest.mock import AsyncMock, patch, MagicMock

from graphql import DocumentNode
from typing import Generator, Dict
from multidict import CIMultiDictProxy, CIMultiDict
from fastapi.requests import Request

from src.sso.dependencies import (
    process_register,
    process_login,
    verify_email,
    get_me,
    change_forget_password,
    update_user_profile,
    change_password,
)
from graphql_client.client import GraphQLClient
from graphql_client.dto import GQLResponse
from src.sso.dto import (
    LoginResponse,
    GetMeResponse,
    RegisterResponse,
    VerifyEmailResponse,
    ChangeForgetPasswordResponse,
    UpdateUserProfileResponse,
    ChangePasswordResponse
)


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
        mock_gql_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_gql_response.result = {"verifyEmail": True}
        mock_gql_response.headers = {"Cookie": "Sfqgreg..."}

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

        result: VerifyEmailResponse = await verify_email(
            verify_email_token="Test-token-1",
        )

        assert result.error == "Ошибка подтверждения email"
        assert result.result is False
        assert result.cookies == []
        assert result.headers is None

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

        assert result.error == "Refresh token invalid"
        assert result.user is None


class TestChangeForgetPassword:
    @pytest.mark.asyncio
    async def test_change_forget_password_success(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {"forget_password_token": "test_change_pass_token"}

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.headers = {"forget_password_token": "test_change_pass_token"}

        mock_gql_client.return_value = mock_response

        result: ChangeForgetPasswordResponse = await change_forget_password(
            request=mock_request,
            new_password="Test_valid_pass"
        )

        mock_gql_client.assert_called_once()

        assert result.error is None
        assert result.headers == {"forget_password_token": "test_change_pass_token"}
        assert result.result is True

        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs

        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "forgetPasswordToken": "test_change_pass_token",
                "newPassword": "Test_valid_pass",
            }
        }

    @pytest.mark.asyncio
    async def test_change_forget_password_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {"forget_password_token": "test_change_pass_token"}

        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = FailedPrecondition desc = New password can not be equal to old password"}
        )

        result: ChangeForgetPasswordResponse = await change_forget_password(
            request=mock_request,
            new_password="Unvalid_password"
        )

        mock_gql_client.assert_called_once()

        assert result.error == "Новый пароль идентичен старому"


class TestUpdateUserProfile:
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.headers = {"editProfileStatus": True}

        mock_gql_client.return_value = mock_response

        result: UpdateUserProfileResponse = await update_user_profile(
            request=mock_request,
            username="Correct_username",
            phone="+79995554433",
            telegram="@HMTMSupport",
            avatar=None,
        )

        mock_gql_client.assert_called_once()

        assert result.result is True
        assert result.error is None
        assert result.headers == mock_response.headers

        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs
        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "displayName": "Correct_username",
                "phone": "+79995554433",
                "telegram": "@HMTMSupport",
                "avatar": None
            }
        }

    @pytest.mark.asyncio
    async def test_update_user_profile_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)

        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = FailedPrecondition desc = display name not meet the requirements"}
        )

        result: UpdateUserProfileResponse = await update_user_profile(
            request=mock_request,
            username="Unc",
            phone="+79995554433",
            telegram="@HMTMSupport",
            avatar=None,
        )

        mock_gql_client.assert_called_once()

        assert result.result is False
        assert result.headers is None
        assert result.error == "Имя пользователя не может быть короче 4-х символов"


class TestChangePassword:
    @pytest.mark.asyncio
    async def test_change_password_success(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.headers = {"changePasswordStatus": True}

        mock_gql_client.return_value = mock_response

        result: ChangePasswordResponse = await change_password(
            request=mock_request,
            old_password="old_password",
            new_password="new_correct_password",
        )

        mock_gql_client.assert_called_once()

        assert result.result is True
        assert result.error is None
        assert result.headers == mock_response.headers

        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs
        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "newPassword": "new_correct_password",
                "oldPassword": "old_password",
            }
        }

    @pytest.mark.asyncio
    async def test_change_password_failure(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = Internal desc = wrong password"}
        )

        result: ChangePasswordResponse = await change_password(
            request=mock_request,
            old_password="old_incorrect_password",
            new_password="new_password",
        )

        mock_gql_client.assert_called_once()
        assert result.result is False
        assert result.headers is None
        assert result.error == "Вы ввели неправильный текущий пароль"

        call_kwargs: Dict[str, str] = mock_gql_client.call_args.kwargs
        assert isinstance(call_kwargs["query"], DocumentNode)
        assert call_kwargs["variable_values"] == {
            "input": {
                "newPassword": "new_password",
                "oldPassword": "old_incorrect_password",
            }
        }
