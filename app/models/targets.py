from ..db import db
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from sqlalchemy import DateTime, func


class Targets(db.Model):
    __tablename__ = "targets"
    id = db.Column(db.Integer, primary_key=True)

    slack_user_id = db.Column(db.String(80), unique=True, nullable=False)
    clickup_spaces = db.Column(ARRAY(db.String(80)), nullable=False)

    ios_teammates = db.Column(JSON, nullable=True)
    web_teammates = db.Column(JSON, nullable=True)
    android_teammates = db.Column(JSON, nullable=True)
    backend_teammates = db.Column(JSON, nullable=True)
    product_manager_teammates = db.Column(JSON, nullable=True)
    engineering_manager_teammates = db.Column(JSON, nullable=True)
    product_designer_teammates = db.Column(JSON, nullable=True)

    created_at = db.Column(DateTime, default=func.now())

    @classmethod
    def get_targets(cls, slack_user_id):
        targets = cls.query.filter(cls.slack_user_id == slack_user_id).first()
        return targets
