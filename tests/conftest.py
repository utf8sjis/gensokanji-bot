import pytest

from app import app


@pytest.fixture
def app_client():
    with app.test_client() as client:
        yield client
