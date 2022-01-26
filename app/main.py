import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from botjobs import bot_job


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='Asia/Tokyo')
    scheduler.add_job(bot_job, IntervalTrigger(minutes=60))
    scheduler.start()
