from ..db import db
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(80), unique=True, nullable=False)
    slack_team_id = db.Column(db.String(80), unique=False, nullable=False)
    slack_user_name = db.Column(db.String(120), nullable=False)

    clickup_token = db.Column(db.String(120), unique=True)
    clickup_user_id = db.Column(db.String(80), unique=True, nullable=True)
    clickup_user_name = db.Column(db.String(120), nullable=True)

    clickup_workspaces = db.Column(JSON, nullable=True)

    @classmethod
    def get_member(cls,slack_user_id):
        user = cls.query.filter(cls.slack_user_id==slack_user_id).first()
        return user