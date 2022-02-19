import os

from dotenv import load_dotenv


load_dotenv(override=True)

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_KEY_SECRET = os.getenv('TWITTER_API_KEY_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
DATABASE_URL = os.getenv('DATABASE_URL')
LOCAL_DB_USER = os.getenv('LOCAL_DB_USER')
LOCAL_DB_PASS = os.getenv('LOCAL_DB_PASS')
