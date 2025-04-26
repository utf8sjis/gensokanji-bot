import threading
import time

import schedule

from bot import Bot
from constants import DATA_DIR


def job() -> None:
    bot = Bot(DATA_DIR)
    bot.post_regular_tweet()


def setup_schedule() -> None:
    # Scheduled at 30 minutes past each hour
    schedule.every().hour.at(":30").do(job)


def run_schedule() -> None:
    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler() -> None:
    setup_schedule()
    threading.Thread(target=run_schedule, daemon=True).start()
