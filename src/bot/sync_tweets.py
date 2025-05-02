from loguru import logger

from api_clients.database_api import DatabaseAPI
from bot.utils import get_all_tweets_from_file
from config import get_settings
from models.tweet import TweetItem


def _get_changes(
    file_tweets: list[TweetItem], db_tweets: list[TweetItem]
) -> tuple[list[str], list[TweetItem], list[TweetItem]]:
    file_tweet_ids = set(tweet.id for tweet in file_tweets)
    db_tweet_ids = set(tweet.id for tweet in db_tweets)

    deleted_tweet_ids = list(db_tweet_ids - file_tweet_ids)

    new_tweets = []
    updated_tweets = []
    for file_tweet in file_tweets:
        if file_tweet.id not in db_tweet_ids:
            new_tweets.append(file_tweet)
            continue

        db_tweet = next(t for t in db_tweets if t.id == file_tweet.id)
        if file_tweet != db_tweet:
            updated_tweets.append(file_tweet)

    return deleted_tweet_ids, new_tweets, updated_tweets


def _update_database(
    db: DatabaseAPI,
    deleted_tweet_ids: list[str],
    new_tweets: list[TweetItem],
    updated_tweets: list[TweetItem],
) -> None:
    if deleted_tweet_ids:
        db.delete_tweets(deleted_tweet_ids)
        logger.info(f"Deleted {len(deleted_tweet_ids)} tweet(s) from the database")

    if new_tweets or updated_tweets:
        db.update_tweets(new_tweets + updated_tweets)
        if new_tweets:
            logger.info(f"Added {len(new_tweets)} new tweet(s) to the database")
        if updated_tweets:
            logger.info(f"Updated {len(updated_tweets)} tweet(s) in the database")


def sync_tweets() -> None:
    """Synchronize tweets between the database and local file."""
    settings = get_settings()
    db = DatabaseAPI(settings)

    file_tweets = get_all_tweets_from_file()
    db_tweets = db.get_all_tweets()

    changes = _get_changes(file_tweets, db_tweets)
    if not any(changes):
        logger.info("No changes detected in tweets")
    else:
        _update_database(db, *changes)

    logger.info("✅ Tweet content sync completed")
