from unittest.mock import patch

import pytest


@pytest.fixture
def app_client():
    with patch("app.start_scheduler"):
        from app import create_app

        app = create_app()

        with app.test_client() as client:
            yield client


class TestApp:
    @staticmethod
    def test_hello_world(app_client):
        # When:
        response = app_client.get("/")

        # Then:
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "Hello, World!"
