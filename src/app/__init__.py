from flask import Flask

from app.routes import register_routes
from bot.scheduler import start_scheduler


def create_app() -> Flask:
    app = Flask(__name__)
    register_routes(app)

    start_scheduler()

    return app
