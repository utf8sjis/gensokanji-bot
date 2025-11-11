import os
from pathlib import Path

_BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_RESOURCES_DIR = _BASE_DIR / "resources"

TWEETS_PATH = _RESOURCES_DIR / "tweet_content/tweets.yml"
TWEET_IMAGES_DIR = _RESOURCES_DIR / "tweet_content/images"

MAX_RETRIES = 5
