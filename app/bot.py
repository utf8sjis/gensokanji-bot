import time
import random
import csv
import json
import datetime

from api.twitter import put_tweet
from api.gdrive import download_file, upload_file


TWEETS_FILE_PATH = 'app/data/tweets.tsv'
TMP_DIR_PATH = '/tmp/'
TWEETED_DATA_FILE_NAME = 'tweeted_id_list.json'
LOG_FILE_NAME = 'log.txt'


# ログの出力
def output_log(text):
    dt_now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9)))
    if download_file(TMP_DIR_PATH, LOG_FILE_NAME):
        with open(TMP_DIR_PATH + LOG_FILE_NAME, 'a') as f:
            f.write('{} {}\n'.format(dt_now.isoformat(timespec='seconds'), text))
        upload_file(TMP_DIR_PATH, LOG_FILE_NAME)


# ツイートのデータの読み込み
def read_tweets():
    # ツイートの読み込み
    with open(TWEETS_FILE_PATH, encoding='utf-8', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)

        tweet_list = []
        for row in reader:
            tweet = {}
            for key, value in zip(header, row):
                tweet[key] = value.replace('\\n', '\n')
            tweet_list.append(tweet)

    # ツイート済みIDリストの作成
    if download_file(TMP_DIR_PATH, TWEETED_DATA_FILE_NAME):
        with open(TMP_DIR_PATH + TWEETED_DATA_FILE_NAME, 'r') as f:
            tweeted_id_list = json.load(f)['tweeted_id_list']
    else:
        tweeted_id_list = []

    return tweet_list, tweeted_id_list


# 未ツイートのツイートのインデクスを返す
def not_tweeted_indices(tweet_list, tweeted_id_list):
    return [i for i, tweet in enumerate(tweet_list)
            if tweet['id'] not in tweeted_id_list]


# ジョブ
def bot_job():
    while True:
        # ツイートのデータの読み込み
        tweet_list, tweeted_id_list = read_tweets()

        # ツイート候補のインデクス
        next_indices = not_tweeted_indices(tweet_list, tweeted_id_list)

        # もし候補が無ければ（一巡）データを初期化し再読み込み
        if next_indices:
            break
        else:
            output_log('tweets have come full circle')
            with open(TMP_DIR_PATH + TWEETED_DATA_FILE_NAME, 'w') as f:
                f.write(json.dumps({
                    'length': 0,
                    'tweeted_id_list': [],
                }, indent=4))
            upload_file(TMP_DIR_PATH, TWEETED_DATA_FILE_NAME)

    while True:
        # ツイート候補を無作為に取り出しツイート
        index = random.choice(next_indices)
        is_success, api_code = put_tweet(tweet_list[index])

        # ツイートに成功したらツイート済みIDリストを更新しダンプ
        # ツイートに失敗したら10秒待ってやりなおし
        if is_success:
            tweeted_id_list.append(tweet_list[index]['id'])
            with open(TMP_DIR_PATH + TWEETED_DATA_FILE_NAME, 'w') as f:
                f.write(json.dumps({
                    'length': len(tweeted_id_list),
                    'tweeted_id_list': tweeted_id_list,
                }, indent=4))
            upload_file(TMP_DIR_PATH, TWEETED_DATA_FILE_NAME)
            break
        else:
            if api_code == 187:  # 連続ツイートの拒否
                output_log('[ERROR] Twitter API: code {} - status is a duplicate'.format(api_code))
            elif api_code == 186:  # ツイート文字数オーバー
                output_log('[ERROR] Twitter API: code {} - tweet needs to be a bit shorter'.format(api_code))
            else:
                output_log('[ERROR] Twitter API: code {}'.format(api_code))
            time.sleep(10)
