from os import urandom
from flask import Flask
from .db import init_db,migrate,db
from .oauth import init_oauth
from .routes import register_routes
from .config import Config

def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(24)
    app.config.from_object(Config)

    init_db(app)
    init_oauth(app)
    register_routes(app)

    migrate.init_app(app, db)

    return app

