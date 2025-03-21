import pytest

from fastapi.testclient import TestClient

from src.main import app as fastapi_app


@pytest.fixture(scope="function", autouse=True)
def test_app():
    return TestClient(app=fastapi_app)


class TestPages:
    @pytest.mark.parametrize(
        "path, status, context",
        [
            ("/", 200, "text/html"),  # Test: homepage
            ("/sso/register", 200, "text/html"),  # Test: register_page
            ("/sso/login", 200, "text/html"),  # Test: login_page
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
        response = test_app.get(path)

        """Сверяем, что получили страницы корректно """
        assert response.status_code == status
        assert "text/html" in response.headers["Content-Type"]
