import pytest

from fastapi.testclient import TestClient
from httpx import Response as httpx_Response
from src.main import app as fastapi_app


@pytest.fixture(scope="function", autouse=True)
def test_app() -> TestClient:
    return TestClient(app=fastapi_app)


class TestPages:
    @pytest.mark.parametrize(
        "path, status, context",
        [
            ("/", 200, "text/html"),
            ("/sso/register", 200, "text/html"),
            ("/sso/login", 200, "text/html"),
            ("/profile/me", 200, "text/html"),
            ("/sso/logout", 200, "text/html"),
            ("/sso/verify-email-letter-form", 200, "text/html"),
        ]
    )
    def test_get_routers(
            self,
            path: str,
            status: int,
            context: str,
            test_app: TestClient
    ) -> None:
        """Получаем ответ от тестового клиента"""
        response: httpx_Response = test_app.get(path)

        """Сверяем, что получили страницы корректно """
        assert response.status_code == status
        assert "text/html" in response.headers["Content-Type"]
