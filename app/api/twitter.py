import tweepy

import config


# ツイートする
def put_tweet(tweet):
    # 認証
    auth = tweepy.OAuthHandler(
        config.TWITTER_API_KEY,
        config.TWITTER_API_KEY_SECRET)
    auth.set_access_token(
        config.TWITTER_ACCESS_TOKEN,
        config.TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # ツイート（例外が発生したらエラーコードを返す）
    try:
        if tweet['images']:
            media_ids = [
                api.media_upload(path).media_id_string for path in tweet['images']]
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
