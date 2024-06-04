from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()

def init_db(app:Flask):
    # Configure the PostgreSQL database URI
    # Initialize SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.postgres_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app=app)

    @app.before_request
    def create_tables():
        db.create_all()

    if not test_db_connection(app,db):
        app.logger.error("Exiting due to database connection failure")
        exit(1)


def test_db_connection(app:Flask,db):
    try:
        # 嘗試進行簡單的數據庫查詢
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            app.logger.info("Database connection successful")
    except Exception as e:
        app.logger.error(f"Database connection failed: {e}")
        return False
    return True