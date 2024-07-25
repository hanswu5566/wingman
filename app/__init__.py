from os import urandom
from flask import Flask
from .db import init_db, migrate, db
from .oauth import init_oauth

from .extensions import celery_instance, make_celery
from .config import Config
from .logger import logger
from .models import *
from .blueprints.slack_auth import slack_auth_bp
from .blueprints.slack import slack_bp
from .blueprints.clickup_auth import clickup_auth_bp

# from .tasks import register_tasks


def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(24)
    app.config.from_object(Config)

    init_db(app)
    init_oauth(app)

    migrate.init_app(app, db)

    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)

    app.app_context().push()
    app.register_blueprint(slack_auth_bp, url_prefix="/slackAuth")
    app.register_blueprint(slack_bp, url_prefix="/slack")
    app.register_blueprint(clickup_auth_bp, url_prefix="/clickup")

    return app


app = create_app()
celery_instance = make_celery(app)
