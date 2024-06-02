import os

import tweepy


class TwitterAPI:
    def __init__(self, tweets_data_dir, api_key, api_key_secret, access_token, access_token_secret):
        """Operate using Twitter API.

        Args:
            tweets_data_dir (str): Path to the directory of tweets data.
            api_key (str): Twitter API customer key.
            api_key_secret (str): Twitter API customer key (secret).
            access_token (str): Twitter API authentication token.
            access_token_secret (str): Twitter API authentication token (secret).

        """
        self.tweets_data_dir = tweets_data_dir
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def post_tweet(self, tweet):
        """Post the tweet.

        Args:
            tweet (dict): Text and image data of the tweet.

        Returns:
            bool: True if successful, false otherwise.
            int: -1 if successful, otherwise Twitter API error code.
                (https://developer.twitter.com/en/support/twitter-api/error-troubleshooting).

        """
        api = self._api()
        client = self._client()

        try:
            if tweet["images"]:
                media_ids = [
                    api.media_upload(os.path.join(self.tweets_data_dir, "img", file_name)).media_id_string
                    for file_name in tweet["images"]
                ]
                client.create_tweet(text=tweet["text"], media_ids=media_ids)
            else:
                client.create_tweet(text=tweet["text"])
        except tweepy.errors.HTTPException as e:
            import traceback

            traceback.print_exc()
            if e.api_codes:
                return False, e.api_codes[0]
            else:
                return False, -1

        return True, -1

    def _api(self):
        """Get Twitter API v1.1 interface.

        Returns:
            API: Twitter API v1.1 interface.

        """
        auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def _client(self):
        """Get Twitter API v2 client.

        Returns:
            Client: Twitter API v2 client.

        """
        return tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_key_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
        )
