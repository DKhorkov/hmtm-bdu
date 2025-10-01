from typing import Generator
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from multidict import CIMultiDict, CIMultiDictProxy

from graphql_client import GraphQLClient
from graphql_client.dto import GQLResponse
from src.core.common.dto import GetMeResponse


@pytest.fixture(scope="function")
def mock_gql_client() -> Generator[AsyncMock, None, None]:
    """Фикстура через декоратор @patch не работает из-за особенностей pytest-а"""
    with patch.object(target=GraphQLClient, attribute="execute", new_callable=AsyncMock) as mock:
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


@pytest.fixture(scope="function")
def mock_get_me() -> Generator[MagicMock, None, None]:
    mock_refresh_tokens: MagicMock = MagicMock(spec=GetMeResponse)
    mock_refresh_tokens.error = None

    mock_access_cookie = MagicMock()
    mock_access_cookie.KEY = "accessToken"
    mock_access_cookie.VALUE = "Egrele'h..."

    mock_refresh_cookie = MagicMock()
    mock_refresh_cookie.KEY = "refreshToken"
    mock_refresh_cookie.VALUE = "Egrele'h..."

    mock_refresh_tokens.cookies = [mock_access_cookie, mock_refresh_cookie]

    yield mock_refresh_tokens


@pytest.fixture(scope="function")
def mock_gql_user_response_by_id() -> Generator[MagicMock, None, None]:
    mock_gql_user_response: MagicMock = MagicMock(spec=GQLResponse)
    mock_gql_user_response.result = {
        "user": {
            "id": 777,
            "displayName": "<NAME>",
            "email": "<EMAIL>",
            "phone": "<PHONE>",
            "telegram": "<TELEGRAM>",
            "avatar": "<AVATAR>",
            "createdAt": "2025-04-27T08:10:35.388787Z"
        }
    }

    yield mock_gql_user_response


@pytest.fixture(scope="function")
def mock_gql_user_response_by_email() -> Generator[MagicMock, None, None]:
    mock_gql_user_response: MagicMock = MagicMock(spec=GQLResponse)
    mock_gql_user_response.result = {
        "userByEmail": {
            "id": 777,
            "displayName": "<NAME>",
            "email": "<EMAIL>",
            "phone": "<PHONE>",
            "telegram": "<TELEGRAM>",
            "avatar": "<AVATAR>",
            "createdAt": "2025-04-27T08:10:35.388787Z"
        }
    }

    yield mock_gql_user_response


@pytest.fixture(scope="function")
def mock_gql_master_response() -> Generator[MagicMock, None, None]:
    mock_gql_master_response: MagicMock = MagicMock(spec=GQLResponse)
    mock_gql_master_response.result = {
        "masterByUser": {
            "id": 222,
            "info": "<INFO>",
            "createdAt": "2025-04-27T08:10:35.388787Z",
            "updatedAt": "2025-04-27T08:10:35.388787Z"
        }
    }

    yield mock_gql_master_response
