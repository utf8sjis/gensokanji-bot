from flask import Flask
from flask_apscheduler import APScheduler

from bot import Bot


TWEETS_DATA_DIR = 'data'


app = Flask(__name__)
scheduler = APScheduler()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@scheduler.task('cron', id='do_job', minute=30)
# @scheduler.task('interval', id='do_job', minutes=5)
def job():
    bot = Bot(TWEETS_DATA_DIR)
    bot.post_regular_tweet()

scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run()
