from bot import Bot
from flask import Flask
from flask_apscheduler import APScheduler

TWEETS_DATA_DIR = "data"


app = Flask(__name__)
scheduler = APScheduler()


@app.route("/")
def hello_world() -> str:
    return "Hello, World!"


@scheduler.task("cron", id="do_job", minute=30)
# @scheduler.task('interval', id='do_job', minutes=5)
def job() -> None:
    bot = Bot(TWEETS_DATA_DIR)
    bot.post_regular_tweet()


scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    app.run()
