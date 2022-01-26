import os
from apscheduler.schedulers.blocking import BlockingScheduler

from botjobs import bot_job


if __name__ == '__main__':
    os.makedirs('tmp', exist_ok=True)

    scheduler = BlockingScheduler(timezone='Asia/Tokyo')
    scheduler.add_job(bot_job, 'interval', minutes=60)
    scheduler.start()
