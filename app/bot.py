import time
import random
import csv
import json

from api.twitter import put_tweet
from api.gdrive import download_file, upload_file


TWEETS_FILE_PATH = 'app/data/tweets.tsv'
TMP_DIR_PATH = '/tmp/'
TMP_FILE_NAME = 'tweeted_id_list.json'


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
    if download_file(TMP_DIR_PATH, TMP_FILE_NAME):
        with open(TMP_DIR_PATH + TMP_FILE_NAME, 'r') as f:
            tweeted_id_list = json.load(f)
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
            print('gensokanji log: [notice] tweets have come full circle')
            with open(TMP_DIR_PATH + TMP_FILE_NAME, 'w') as f:
                f.write(json.dumps([]))
            upload_file(TMP_DIR_PATH, TMP_FILE_NAME)

    while True:
        # ツイート候補を無作為に取り出しツイート
        index = random.choice(next_indices)
        is_success, api_code = put_tweet(tweet_list[index])

        # ツイートに成功したらツイート済みIDリストを更新しダンプ
        # ツイートに失敗したら10秒待ってやりなおし
        if is_success:
            tweeted_id_list.append(tweet_list[index]['id'])
            with open(TMP_DIR_PATH + TMP_FILE_NAME, 'w') as f:
                f.write(json.dumps(tweeted_id_list))
            upload_file(TMP_DIR_PATH, TMP_FILE_NAME)
            break
        else:
            if api_code == 187:  # 連続ツイートの拒否
                print('gensokanji log: [error] status is a duplicate')
            elif api_code == 186:  # ツイート文字数オーバー
                print('gensokanji log: [error] tweet needs to be a bit shorter')
            else:
                print('gensokanji log: [error] other twitter exception')
            time.sleep(10)
