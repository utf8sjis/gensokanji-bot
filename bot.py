import os
import time
import random
import csv
from datetime import datetime, timezone, timedelta

import config
from api import TwitterAPI, BotDatabase


class Bot():
    def __init__(self, tweets_data_dir):
        self.tweets_data_dir = tweets_data_dir
        self.tweets = self._read_tweets(tweets_data_dir)

    def post_regular_tweet(self):
        # 定期ツイート
        twitter_api = TwitterAPI(self.tweets_data_dir,
                                 config.TWITTER_API_KEY,
                                 config.TWITTER_API_KEY_SECRET,
                                 config.TWITTER_ACCESS_TOKEN,
                                 config.TWITTER_ACCESS_TOKEN_SECRET)
        bot_database = BotDatabase(config.DATABASE_URL, config.DATABASE_KEY)

        while True:
            # ツイート済みのID
            posted_data = bot_database.get_posted_data()
            posted_ids = posted_data['tweeted_data_json']['tweeted_id_list']

            # ツイート候補のインデクス
            candidate_indices = self._get_unposted_indices(posted_ids)

            # もし候補が無ければ（一巡）データを初期化し再読み込み
            if candidate_indices:
                break
            else:
                self._output_log('tweets have come full circle')
                bot_database.update_posted_data(self._make_posted_data([]))

        while True:
            # ツイート候補を無作為に取り出しツイート
            candidate_index = random.choice(candidate_indices)
            is_success, api_code = twitter_api.post_tweet(
                self.tweets[candidate_index])

            # ツイートに成功したらツイート済みIDリストを更新
            # ツイートに失敗したら10秒待ってやりなおし
            if is_success:
                posted_ids.append(self.tweets[candidate_index]['id'])
                bot_database.update_posted_data(self._make_posted_data(posted_ids))
                break
            else:
                if api_code == 187:  # 連続ツイートの拒否
                    self._output_log('[ERROR] Twitter API: code {} - status is a duplicate'.format(api_code))
                elif api_code == 186:  # ツイート文字数オーバー
                    self._output_log('[ERROR] Twitter API: code {} - tweet needs to be a bit shorter'.format(api_code))
                else:
                    self._output_log('[ERROR] Twitter API: code {}'.format(api_code))
                time.sleep(10)

    def _read_tweets(self, tweets_data_dir):
        # ツイートのデータの読み込み
        tweets_data_path = os.path.join(tweets_data_dir, 'tweets.tsv')
        with open(tweets_data_path, encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)

            tweets = []
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
                tweets.append(tweet)

        return tweets

    def _get_unposted_indices(self, posted_ids):
        # 未ツイートのツイートのインデクスを返す
        return [index for index, tweet in enumerate(self.tweets)
                if tweet['id'] not in posted_ids]

    def _make_posted_data(self, posted_ids):
        posted_tweets_data = {
            'tweeted': len(posted_ids),
            'tweeted_id_list': posted_ids,
        }
        posted_data = {
            'updated_at': str(self._get_current_datetime()),
            'tweeted_data_json': posted_tweets_data
        }
        return posted_data

    def _output_log(self, text):
        # ログの出力
        print('{} {}\n'.format(self._get_current_datetime(), text))

    def _get_current_datetime(self):
        # 現在の日付と時刻を返す
        return datetime.now(timezone(timedelta(hours=9)))