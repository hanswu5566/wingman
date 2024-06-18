from ..db import db
from sqlalchemy.dialects.postgresql import ARRAY

class Teammates(db.Model):
    __tablename__ = 'teammates'
    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(80), unique=True, nullable=False)
    
    ios_teammates = db.Column(ARRAY(db.String(80)), nullable=True)
    web_teammates = db.Column(ARRAY(db.String(80)), nullable=True)
    android_teammates = db.Column(ARRAY(db.String(80)), nullable=True)
    backend_teammates = db.Column(ARRAY(db.String(80)), nullable=True)
    product_manager_teammates = db.Column(ARRAY(db.String(80)), nullable=True)
    product_designer_teammates = db.Column(ARRAY(db.String(80)), nullable=True)

    @classmethod
    def get_teammates(cls,slack_user_id):
        teammates = cls.query.filter(cls.slack_user_id==slack_user_id).first()
        return teammates