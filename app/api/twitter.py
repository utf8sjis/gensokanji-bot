import tweepy


class TwitterAPI():

    def __init__(self, api_key, api_key_secret,
                 access_token, access_token_secret):
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def _access(self):
        # 認証
        auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth, wait_on_rate_limit=True)

    def put_tweet(self, tweet):
        # ツイートする
        api = self._access()

        try:
            if tweet['images']:
                media_ids = [
                    api.media_upload(path).media_id_string
                    for path in tweet['images']]
                api.update_status(tweet['text'], media_ids=media_ids)
            else:
                api.update_status(tweet['text'])
        except tweepy.errors.HTTPException as e:
            import traceback
            traceback.print_exc()
            if e.api_codes:
                return False, e.api_codes[0]
            else:
                return False, -1

        return True, -1
