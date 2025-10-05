from bot.bot import Bot
from bot.sync_tweets import sync_tweets

if __name__ == "__main__":
    sync_tweets()
    bot = Bot()
    bot.post_regular_tweet()
