import os
import time
from unittest.mock import patch

import pytest

from app import app


@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    with patch.dict(
        os.environ,
        {
            "TWITTER_API_KEY": "dummy_key",
            "TWITTER_API_KEY_SECRET": "dummy_key_secret",
            "TWITTER_ACCESS_TOKEN": "dummy_token",
            "TWITTER_ACCESS_TOKEN_SECRET": "dummy_token_secret",
            "DATABASE_URL": "dummy_db_url",
            "DATABASE_KEY": "dummy_db_key",
        },
    ):
        yield


@pytest.fixture
def app_client():
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_time_sleep():
    with patch.object(time, "sleep") as mock:
        yield mock
