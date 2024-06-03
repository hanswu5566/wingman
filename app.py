from os import urandom
from flask import Flask
from dotenv import load_dotenv
from db import init_db,migrate,db
from oauth import init_oauth
from routes import register_routes



def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(24)

    load_dotenv()
    init_db(app)
    init_oauth(app)
    register_routes(app)

    migrate.init_app(app, db)

    return app

