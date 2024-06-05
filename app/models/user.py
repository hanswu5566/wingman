from ..db import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    slack_user_id = db.Column(db.String(80), unique=True, nullable=False)
    team_id = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)


    @classmethod
    def is_member(cls,slack_user_id)->bool:
        user = cls.query.filter(slack_user_id=slack_user_id).first()
        return user is not None