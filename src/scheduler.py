import threading
import time

import schedule
from loguru import logger
from pytz import timezone

from bot.bot import Bot
from bot.sync_tweets import sync_tweets


def job():
    bot = Bot()
    bot.post_regular_tweet()


def setup_schedule():
    # Scheduled at 7:00 AM to 11:00 PM every day
    # Since November 2024, the daily post cap has been set to 17
    time_strs = [f"{hour:02d}:00" for hour in range(7, 24)]
    for time_str in time_strs:
        schedule.every().day.at(time_str, timezone("Asia/Tokyo")).do(job)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    sync_tweets()
    setup_schedule()
    threading.Thread(target=run_schedule, daemon=True).start()
    logger.info("Scheduler started")
