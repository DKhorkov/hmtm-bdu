import pytest

pytestmark = pytest.mark.usefixtures("mock_get_me", "mock_gql_client")

from unittest.mock import AsyncMock, patch, MagicMock

from graphql import DocumentNode
from typing import Dict
from fastapi.requests import Request
from src.profile.dependencies import (
    change_password,
    update_user_profile,
    master_by_user,
    update_master,
    register_master
)
from graphql_client.dto import GQLResponse
from src.profile.dto import (
    UpdateUserProfileResponse,
    ChangePasswordResponse,
    GetUserIsMasterResponse,
    UpdateMasterResponse,
    RegisterMasterResponse
)


class TestUpdateUserProfile:
    @pytest.mark.asyncio
    async def test_update_user_profile_success(
            self,
            mock_gql_client: AsyncMock,
            mock_get_me: MagicMock
    ) -> None:
        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.headers = {"editProfileStatus": True}

        mock_gql_client.return_value = mock_response
        mock_request: MagicMock = MagicMock(spec=Request)

        result: UpdateUserProfileResponse = await update_user_profile(
            username="Correct_username",
            phone="+79995554433",
            telegram="@HMTMSupport",
            avatar=None,
            request=mock_request,
            current_user=mock_get_me,
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
    async def test_update_user_profile_failure(
            self,
            mock_gql_client: AsyncMock,
            mock_get_me: MagicMock
    ) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = FailedPrecondition desc = display name not meet the requirements"}
        )
        mock_request: MagicMock = MagicMock(spec=Request)

        result: UpdateUserProfileResponse = await update_user_profile(
            current_user=mock_get_me,
            username="Unc",
            phone="+79995554433",
            telegram="@HMTMSupport",
            avatar=None,
            request=mock_request
        )

        mock_gql_client.assert_called_once()

        assert result.result is False
        assert result.headers is None
        assert result.error == "Имя пользователя не может быть короче 4-х символов"


class TestChangePassword:
    @pytest.mark.asyncio
    async def test_change_password_success(self, mock_gql_client: AsyncMock, mock_get_me: MagicMock) -> None:
        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.headers = {"changePasswordStatus": True}
        mock_request: MagicMock = MagicMock(spec=Request)

        mock_gql_client.return_value = mock_response

        result: ChangePasswordResponse = await change_password(
            request=mock_request,
            old_password="old_password",
            new_password="new_correct_password",
            current_user=mock_get_me
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
    async def test_change_password_failure(self, mock_gql_client: AsyncMock, mock_get_me: MagicMock) -> None:
        mock_gql_client.side_effect = Exception(
            {"message": "rpc error: code = Internal desc = wrong password"}
        )
        mock_request: MagicMock = MagicMock(spec=Request)

        result: ChangePasswordResponse = await change_password(
            request=mock_request,
            old_password="old_incorrect_password",
            new_password="new_password",
            current_user=mock_get_me
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


class TestGetMasterByUser:
    @pytest.mark.asyncio
    async def test_get_master_by_user_success(self, mock_gql_client: AsyncMock) -> None:
        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {
            "masterByUser": {
                "id": "1",
                "info": "Test_master",
                "createdAt": "2025-04-27T08:10:35.388787Z",
                "updatedAt": "2025-04-27T08:10:35.388787Z",
            }
        }

        mock_request = MagicMock(spec=Request)
        mock_request.cookies = {"accessToken": "...", "refreshToken": "..."}

        mock_gql_client.return_value = mock_response

        result: GetUserIsMasterResponse = await master_by_user(
            user_id=mock_response.result["masterByUser"]["id"],
            request=mock_request,
        )

        assert result.master.id == "1"  # type: ignore[union-attr]
        assert result.master.info == "Test_master"  # type: ignore[union-attr]
        assert result.master.created_at == "27.04.2025"  # type: ignore[union-attr]
        assert result.master.updated_at == "27.04.2025"  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_get_master_by_user_failure_with_no_cookies(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {}

        result: GetUserIsMasterResponse = await master_by_user(
            user_id="1",
            request=mock_request
        )

        assert result.result is False
        assert result.error == "Пользователь не найден"

    @pytest.mark.asyncio
    async def test_get_master_by_user_failure_with_no_master(self, mock_gql_client: AsyncMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {"accessToken": "...", "refreshToken": "..."}

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {
            "errors": [
                {
                    "message": "rpc error: code = NotFound desc = master not found",
                    "path": [
                        "masterByUser"
                    ]
                }
            ],
            "data": None
        }
        mock_gql_client.return_value = mock_response

        result: GetUserIsMasterResponse = await master_by_user(
            user_id="1",
            request=mock_request
        )

        assert result.result is False
        assert result.error == "Пользователь не является мастером"


class TestUpdateMaster:
    @pytest.mark.asyncio
    async def test_update_master_success(self, mock_gql_client: AsyncMock, mock_get_me: MagicMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {}

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {"gql_query_status": True}
        mock_response.headers = {}

        mock_master: MagicMock = MagicMock(spec=GetUserIsMasterResponse)
        mock_master.master = MagicMock()
        mock_master.master.id = 1
        mock_master.master.info = "Test_master"
        mock_master.master.created_at = "27.04.2025"
        mock_master.master.updated_at = "27.04.2025"

        with patch('src.profile.dependencies.master_by_user', new=AsyncMock(return_value=mock_master)):
            new_master_info = "New_test_master"
            mock_gql_client.return_value = mock_response

            result: UpdateMasterResponse = await update_master(
                request=mock_request,
                info=new_master_info,
                current_user=mock_get_me
            )

            assert result.result is True

    @pytest.mark.asyncio
    async def test_update_master_failure_with_no_cookies(
            self,
            mock_gql_client: AsyncMock,
            mock_get_me: MagicMock
    ) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {"gql_query_status": True}

        mock_master: MagicMock = MagicMock(spec=GetUserIsMasterResponse)
        mock_master.master.id = 1
        mock_master.master.info = "Test_master"
        mock_master.master.created_at = "27.04.2025"
        mock_master.master.updated_at = "27.04.2025"

        new_master_info = "New_test_master"

        mock_get_me.error = "accessToken not found"

        mock_gql_client.return_value = mock_response

        result: UpdateMasterResponse = await update_master(
            request=mock_request,
            info=new_master_info,
            current_user=mock_get_me
        )

        assert result.result is False
        assert result.error == "Пользователь не найден"

    @pytest.mark.asyncio
    async def test_update_master_failure_with_no_master(
            self,
            mock_gql_client: AsyncMock,
            mock_get_me: MagicMock
    ) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)
        mock_request.cookies = {}  # Добавляем cookies

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {"gql_query_status": True}

        mock_master: MagicMock = MagicMock(spec=GetUserIsMasterResponse)
        mock_master.master = None

        with patch('src.profile.dependencies.master_by_user', new=AsyncMock(return_value=mock_master)):
            new_master_info = "New_test_master"

            result: UpdateMasterResponse = await update_master(
                request=mock_request,
                info=new_master_info,
                current_user=mock_get_me
            )

            assert result.result is False
            assert result.error == "Не удалось найти мастера"


class TestRegisterMaster:
    @pytest.mark.asyncio
    async def test_register_master_success(self, mock_gql_client: AsyncMock, mock_get_me: MagicMock) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {"gql_query_status": True}

        master_info = "New_master"

        result: RegisterMasterResponse = await register_master(
            request=mock_request,
            info=master_info,
            current_user=mock_get_me
        )

        assert result.result is True
        assert result.error is None

    @pytest.mark.asyncio
    async def test_register_master_failure_with_no_cookies(
            self,
            mock_gql_client: AsyncMock,
            mock_get_me: MagicMock
    ) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)

        mock_response: MagicMock = MagicMock(spec=GQLResponse)
        mock_response.result = {"gql_query_status": True}

        mock_get_me.error = "accessToken not found"

        master_info = "New_master"

        result: RegisterMasterResponse = await register_master(
            request=mock_request,
            info=master_info,
            current_user=mock_get_me
        )

        assert result.result is False
        assert result.error == "Пользователь не найден"

    @pytest.mark.asyncio
    async def test_register_master_failure_with_invalid_info(
            self,
            mock_gql_client:
            AsyncMock,
            mock_get_me: MagicMock
    ) -> None:
        mock_request: MagicMock = MagicMock(spec=Request)

        mock_gql_client.return_value = {
            "errors": [
                {"message": "Некорректное поле info"}
            ]
        }

        result: RegisterMasterResponse = await register_master(
            request=mock_request,
            info="New_master",
            current_user=mock_get_me
        )

        assert result.result is False
        assert result.error == "Неизвестная ошибка"
