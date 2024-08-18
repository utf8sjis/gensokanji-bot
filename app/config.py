import os

from dotenv import load_dotenv


load_dotenv(override=True)

TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_KEY_SECRET = os.getenv('TWITTER_API_KEY_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
GOOGLE_API_ACCESS_TOKEN = os.getenv('GOOGLE_API_ACCESS_TOKEN')