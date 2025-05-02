import os
from pathlib import Path

_BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA_DIR = _BASE_DIR / "data"

TWEETS_PATH = _DATA_DIR / "tweets.yml"
TWEET_IMAGES_DIR = _DATA_DIR / "images"
