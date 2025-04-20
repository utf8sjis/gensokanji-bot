import os

from flask import Flask
from flask_apscheduler import APScheduler

from bot import Bot
from constants import BOT_JOB_ID, BOT_JOB_SCHEDULE, DATA_DIR

ENV = os.getenv("ENV", "development")

if ENV == "development":
    from dotenv import load_dotenv

    load_dotenv(override=True)


app = Flask(__name__)
scheduler = APScheduler()


@app.route("/")
def hello_world() -> str:
    return "Hello, World!"


@scheduler.task("cron", id=BOT_JOB_ID, **BOT_JOB_SCHEDULE)
def bot_job() -> None:
    bot = Bot(DATA_DIR)
    bot.post_regular_tweet()


scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    app.run()
