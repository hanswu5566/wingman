from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import postgres_url
import logging

def init_db(app):
    # Configure the PostgreSQL database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = postgres_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    if not test_db_connection(app,db):
        logging.error("Exiting due to database connection failure")
        exit(1)

    return db


def test_db_connection(app,db):
    try:
        # 嘗試進行簡單的數據庫查詢
        with app.app_context():
            db.session.execute(text('SELECT 1'))
            logging.info("Database connection successful")
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return False
    return True