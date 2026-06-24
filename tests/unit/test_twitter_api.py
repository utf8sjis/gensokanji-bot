import json
from unittest.mock import MagicMock, patch
from urllib.request import Request

import pytest

from api_clients.twitter_api import TwitterAPI
from config import Settings
from models.tweet import TweetItem


def _tweet(image_paths: list[str] | None = None) -> TweetItem:
    return TweetItem(
        id="test001",
        type="regular",
        group="test",
        text="テスト",
        image_paths=image_paths or [],
    )


class TestTwitterAPI:
    @staticmethod
    def test_xquik_backend_skips_twitter_client_setup():
        settings = Settings(x_post_backend="xquik")

        with (
            patch.object(TwitterAPI, "_get_api") as mock_get_api,
            patch.object(TwitterAPI, "_get_client") as mock_get_client,
        ):
            TwitterAPI(settings)

        mock_get_api.assert_not_called()
        mock_get_client.assert_not_called()

    @staticmethod
    def test_xquik_backend_posts_to_create_tweet_endpoint():
        settings = Settings(
            x_post_backend="xquik",
            xquik_api_key="test-key",
            xquik_account="@example",
            xquik_create_tweet_url="https://xquik.com/api/v1/x/tweets",
        )
        response = MagicMock()
        response.__enter__.return_value = response

        with patch("api_clients.twitter_api.urlopen", return_value=response) as mock:
            TwitterAPI(settings).post_tweet(_tweet(["https://example.com/media.png"]))

        request = mock.call_args.args[0]
        assert isinstance(request, Request)
        assert request.full_url == "https://xquik.com/api/v1/x/tweets"
        assert request.get_method() == "POST"
        assert request.get_header("X-api-key") == "test-key"
        assert request.get_header("Content-type") == "application/json"
        assert request.data is not None
        assert json.loads(request.data.decode("utf-8")) == {
            "account": "@example",
            "text": "テスト",
            "media": ["https://example.com/media.png"],
        }
        response.read.assert_called_once()

    @staticmethod
    def test_xquik_backend_requires_api_key():
        settings = Settings(x_post_backend="xquik", xquik_account="@example")

        with pytest.raises(ValueError, match="XQUIK_API_KEY"):
            TwitterAPI(settings).post_tweet(_tweet())

    @staticmethod
    def test_xquik_backend_requires_public_media_urls():
        settings = Settings(
            x_post_backend="xquik",
            xquik_api_key="test-key",
            xquik_account="@example",
        )

        with pytest.raises(ValueError, match="public URLs"):
            TwitterAPI(settings).post_tweet(_tweet(["main001.png"]))
