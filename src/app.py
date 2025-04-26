import os

from flask import Flask

from scheduler import start_scheduler

ENV = os.getenv("ENV", "development")

if ENV == "development":
    from dotenv import load_dotenv

    load_dotenv(override=True)


app = Flask(__name__)
start_scheduler()


@app.route("/")
def hello_world() -> str:
    return "Hello, World!"


if __name__ == "__main__":
    app.run()
