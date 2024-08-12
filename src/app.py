from flask import Flask
from flask_apscheduler import APScheduler

from bot import Bot
from constants import DATA_DIR

app = Flask(__name__)
scheduler = APScheduler()


@app.route("/")
def hello_world() -> str:
    return "Hello, World!"


@scheduler.task("cron", id="do_bot_job", minute=30)
def bot_job() -> None:
    bot = Bot(DATA_DIR)
    bot.post_regular_tweet()


scheduler.init_app(app)
scheduler.start()

if __name__ == "__main__":
    app.run()
