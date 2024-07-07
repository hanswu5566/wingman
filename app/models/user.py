from ..db import db
from sqlalchemy import DateTime, func


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(80), unique=True, nullable=False)
    slack_team_id = db.Column(db.String(80), unique=True, nullable=False)
    slack_user_name = db.Column(db.String(120), nullable=False)

    clickup_token = db.Column(db.String(120), unique=True)
    clickup_user_id = db.Column(db.String(80), unique=True, nullable=True)
    clickup_user_name = db.Column(db.String(120), nullable=True)
    clickup_team_id = db.Column(db.String(120), unique=True, nullable=True)
    clickup_team_name = db.Column(db.String(120), nullable=True)

    created_at = db.Column(DateTime, default=func.now())

    @classmethod
    def get_member(cls, slack_user_id):
        user = cls.query.filter(cls.slack_user_id == slack_user_id).first()
        return user
