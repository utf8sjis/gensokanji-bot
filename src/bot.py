import os
import random
import time
from pathlib import Path
from typing import Final

import yaml

from api.database import BotDatabase
from api.twitter import TwitterAPI
from data_models import PostedData, TweetData, TweetDataItem
from utils import get_current_datetime


class Bot:
    def __init__(self, tweets_data_dir: Path) -> None:
        """Bot functions.

        Currently, only the function to post tweets regularly is registered.

        Args:
            tweets_data_dir (Path): Path to the directory of tweets data.

        """
        self.tweets_data_dir: Final = tweets_data_dir

        self.twitter_api_key: Final = os.getenv("TWITTER_API_KEY", "")
        self.twitter_api_key_secret: Final = os.getenv("TWITTER_API_KEY_SECRET", "")
        self.twitter_access_token: Final = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.twitter_access_token_secret: Final = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
        self.database_url: Final = os.getenv("DATABASE_URL", "")
        self.database_key: Final = os.getenv("DATABASE_KEY", "")

        if not all(
            [
                self.twitter_api_key,
                self.twitter_api_key_secret,
                self.twitter_access_token,
                self.twitter_access_token_secret,
                self.database_url,
                self.database_key,
            ]
        ):
            raise ValueError("Environment variables are not set.")

        self.tweets = self._read_tweets()

    def post_regular_tweet(self) -> None:
        """Post a regular tweet."""
        twitter_api = TwitterAPI(
            self.tweets_data_dir,
            self.twitter_api_key,
            self.twitter_api_key_secret,
            self.twitter_access_token,
            self.twitter_access_token_secret,
        )
        bot_database = BotDatabase(self.database_url, self.database_key)

        while True:
            # Get candidates for tweets to post.
            posted_ids = bot_database.get_posted_data().ids
            candidate_indices = self._get_unposted_indices(posted_ids)

            if candidate_indices:
                break
            else:
                # If there are no candidates, initialize data on tweets already posted
                # and reload them (next loop).
                self._output_log("tweets have come full circle")
                bot_database.update_posted_data(PostedData(total=0, ids=[]))

        while True:
            # Post one of the candidates at random.
            candidate_index = random.choice(candidate_indices)
            is_success, api_code = twitter_api.post_tweet(self.tweets[candidate_index])

            if is_success:
                posted_ids.append(self.tweets[candidate_index].id)
                bot_database.update_posted_data(PostedData(total=len(posted_ids), ids=posted_ids))
                break
            else:
                if api_code == 187:
                    self._output_log("[ERROR] Twitter API: code {} - status is a duplicate".format(api_code))
                elif api_code == 186:
                    self._output_log("[ERROR] Twitter API: code {} - tweet needs to be a bit shorter".format(api_code))
                else:
                    self._output_log("[ERROR] Twitter API: code {}".format(api_code))
                time.sleep(10)

    def _read_tweets(self) -> list[TweetDataItem]:
        """Load regular tweets data.

        Returns:
            list: List of regular tweets (text and image data).

        """
        with open(self.tweets_data_dir / "tweets.yml") as f:
            tweets_data = TweetData(**yaml.safe_load(f))

        return tweets_data.tweets

    def _get_unposted_indices(self, posted_ids: list[str]) -> list[int]:
        """Get unposted tweets data.

        Args:
            posted_ids (list): List of IDs of tweets already posted.

        Returns:
            list: Indices in `self.tweets` for unposted tweets.

        """
        return [index for index, tweet in enumerate(self.tweets) if tweet.id not in posted_ids]

    def _output_log(self, text: str) -> None:
        """Output log.

        Args:
            text (str): Log message.

        """
        print("{} {}\n".format(get_current_datetime(), text))
