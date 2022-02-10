from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from bot import bot_job


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='Asia/Tokyo')
    scheduler.add_job(bot_job, CronTrigger(minutes=30))
    scheduler.start()
