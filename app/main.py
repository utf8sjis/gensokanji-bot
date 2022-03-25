from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from bot import BotJob


TWEETS_FILE_PATH = 'app/data/tweets.tsv'


if __name__ == '__main__':
    bot_job = BotJob(TWEETS_FILE_PATH)

    scheduler = BlockingScheduler(timezone='Asia/Tokyo')
    scheduler.add_job(bot_job.regularly_tweet, CronTrigger(minute=30))
    scheduler.start()
