from flask import Flask
from flask_apscheduler import APScheduler

from bot import BotJob


app = Flask(__name__)
scheduler = APScheduler()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@scheduler.task('cron', id='do_job', minute=30)
# @scheduler.task('interval', id='do_job', minutes=5)
def job():
    tweets_file_path = 'data/tweets.tsv'
    bot_job = BotJob(tweets_file_path)
    bot_job.regularly_tweet()

scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run()
