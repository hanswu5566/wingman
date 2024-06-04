from os import urandom
from flask import Flask
from dotenv import load_dotenv
from app.db import init_db,migrate,db
from app.oauth import init_oauth
from app.routes import register_routes
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.postgres_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    load_dotenv()
    init_db(app)
    init_oauth(app)
    register_routes(app)

    migrate.init_app(app, db)

    return app

