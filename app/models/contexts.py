from ..db import db
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSON


class Contexts(db.Model):
    __tablename__ = "contexts"
    id = db.Column(db.Integer, primary_key=True)

    slack_user_id = db.Column(db.String(80), unique=True, nullable=False, index=True)

    last_clickup_dify_answer = db.Column(JSON, nullable=True)
    created_at = db.Column(DateTime, default=func.now())

    @classmethod
    def get_contexts(cls, slack_user_id):
        contexts = cls.query.filter(cls.slack_user_id == slack_user_id).first()
        return contexts
