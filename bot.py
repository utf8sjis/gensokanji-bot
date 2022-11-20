import os
import time
import random
import csv
from datetime import datetime, timezone, timedelta

import config
from api import TwitterAPI, BotDBQuery


def read_tweets(tweets_data_dir):
    # ツイートのデータの読み込み
    with open(os.path.join(tweets_data_dir, 'tweets.tsv'), encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)

        tweet_list = []
        for row in reader:
            tweet = {'images': []}
            for key, value in zip(header, row):
                if key == 'text':
                    tweet[key] = value.replace('\\n', '\n')
                elif key in ['img1', 'img2', 'img3', 'img4']:
                    if value:
                        tweet['images'].append(value)
                else:
                    tweet[key] = value
            tweet_list.append(tweet)

    return tweet_list


class BotJob():
    def __init__(self, tweets_data_dir):
        self.tweets_data_dir = tweets_data_dir
        self.tweet_list = read_tweets(tweets_data_dir)

    def _datetime_now(self):
        # 現在の日付と時刻を返す
        return datetime.now(timezone(timedelta(hours=9)))

    def _output_log(self, text):
        # ログの出力
        print('{} {}\n'.format(self._datetime_now(), text))

    def _not_tweeted_indices(self, tweeted_id_list):
        # 未ツイートのツイートのインデクスを返す
        return [i for i, tweet in enumerate(self.tweet_list)
                if tweet['id'] not in tweeted_id_list]

    def _make_tweeted_data(self, tweeted_id_list):
        # tweeted_data.jsonのデータを作る
        return {
            'tweeted': len(tweeted_id_list),
            'tweeted_id_list': tweeted_id_list,
        }

    def regularly_tweet(self):
        # 定期ツイート
        twitter_api = TwitterAPI(self.tweets_data_dir,
                                 config.TWITTER_API_KEY,
                                 config.TWITTER_API_KEY_SECRET,
                                 config.TWITTER_ACCESS_TOKEN,
                                 config.TWITTER_ACCESS_TOKEN_SECRET)
        bot_db = BotDBQuery(config.DATABASE_URL, config.DATABASE_KEY)

        while True:
            # ツイート済みのID
            tweeted_id_list = bot_db.get_data()['tweeted_id_list']

            # ツイート候補のインデクス
            next_indices = self._not_tweeted_indices(tweeted_id_list)

            # もし候補が無ければ（一巡）データを初期化し再読み込み
            if next_indices:
                break
            else:
                self._output_log('tweets have come full circle')
                bot_db.update_data(
                    self._datetime_now(), self._make_tweeted_data([]))

        while True:
            # ツイート候補を無作為に取り出しツイート
            index = random.choice(next_indices)
            is_success, api_code = twitter_api.post_tweet(
                self.tweet_list[index])

            # ツイートに成功したらツイート済みIDリストを更新
            # ツイートに失敗したら10秒待ってやりなおし
            if is_success:
                tweeted_id_list.append(self.tweet_list[index]['id'])
                bot_db.update_data(
                    self._datetime_now(), self._make_tweeted_data(tweeted_id_list))
                break
            else:
                if api_code == 187:  # 連続ツイートの拒否
                    self._output_log('[ERROR] Twitter API: code {} - status is a duplicate'.format(api_code))
                elif api_code == 186:  # ツイート文字数オーバー
                    self._output_log('[ERROR] Twitter API: code {} - tweet needs to be a bit shorter'.format(api_code))
                else:
                    self._output_log('[ERROR] Twitter API: code {}'.format(api_code))
                time.sleep(10)
