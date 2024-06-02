import csv
import os
import random
import time

import config
from api import BotDatabase, TwitterAPI
from data_models import PostedData
from utils import get_current_datetime


class Bot:
    def __init__(self, tweets_data_dir: str) -> None:
        """Bot functions.

        Currently, only the function to post tweets regularly is registered.

        Args:
            tweets_data_dir (str): Path to the directory of tweets data.

        """
        self.tweets_data_dir = tweets_data_dir

        self.tweets = self._read_tweets()

    def post_regular_tweet(self) -> None:
        """Post a regular tweet."""
        twitter_api = TwitterAPI(
            self.tweets_data_dir,
            config.TWITTER_API_KEY,
            config.TWITTER_API_KEY_SECRET,
            config.TWITTER_ACCESS_TOKEN,
            config.TWITTER_ACCESS_TOKEN_SECRET,
        )
        bot_database = BotDatabase(config.DATABASE_URL, config.DATABASE_KEY)

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
                posted_ids.append(self.tweets[candidate_index]["id"])
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

    def _read_tweets(self) -> list[dict]:
        """Load regular tweets data.

        Returns:
            list: List of regular tweets (text and image data).

        """
        tweets_data_path = os.path.join(self.tweets_data_dir, "tweets.tsv")
        with open(tweets_data_path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)

            tweets = []
            for row in reader:
                tweet = {"images": []}
                for key, value in zip(header, row):
                    if key == "text":
                        tweet[key] = value.replace("\\n", "\n")
                    elif key in ["img1", "img2", "img3", "img4"]:
                        if value:
                            tweet["images"].append(value)
                    else:
                        tweet[key] = value
                tweets.append(tweet)

        return tweets

    def _get_unposted_indices(self, posted_ids: list[str]) -> list[int]:
        """Get unposted tweets data.

        Args:
            posted_ids (list): List of IDs of tweets already posted.

        Returns:
            list: Indices in `self.tweets` for unposted tweets.

        """
        return [index for index, tweet in enumerate(self.tweets) if tweet["id"] not in posted_ids]

    def _output_log(self, text: str) -> None:
        """Output log.

        Args:
            text (str): Log message.

        """
        print("{} {}\n".format(get_current_datetime(), text))
