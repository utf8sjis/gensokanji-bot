import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from botjobs import bot_job


if __name__ == '__main__':
    os.makedirs('tmp', exist_ok=True)

    scheduler = BlockingScheduler(timezone='Asia/Tokyo')
    scheduler.add_job(bot_job, IntervalTrigger(minutes=60))
    scheduler.start()
