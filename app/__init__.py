from os import urandom
from flask import Flask
from .db import init_db,migrate,db
from .oauth import init_oauth

from .config import Config
from .logger import logger
from .models import *
from .blueprints.auth import auth_bp
from .blueprints.slack import slack_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(24)
    app.config.from_object(Config)

    init_db(app)
    init_oauth(app)

    migrate.init_app(app, db)

    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(slack_bp,url_prefix='/slack')

    return app

