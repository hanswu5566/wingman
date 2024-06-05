from flask import Blueprint, jsonify, session, redirect, url_for
from ..models import User
from ..db import db
from ..oauth import oauth
from slack_sdk import WebClient
from ..config import Config
from ..logger import logger

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/slack/login")
def login():
    return oauth.slack.authorize_redirect(Config.SLACK_REDIRECT_URL)

@auth_bp.route("/slack/logout")
def logout():
    session.pop('slack_token')
    return redirect(url_for('index'))

@auth_bp.route('/slack/login/authorize')
def authorize():
    try:
        token = oauth.slack.authorize_access_token()
        if token is None or not token.get('ok'):
            logger.error("OAuth token is None or not ok")
            return jsonify({"error": "OAuth token is None or not ok"}), 500

        access_token = token['access_token']
        slack_user_id = token['authed_user']['id']
        user = User.query.filter_by(slack_user_id=slack_user_id).first()
    
        if not user:
            client = WebClient(token=access_token)
            info = client.users_info(user=slack_user_id)
            if not info['ok']:
                logger.error("Failed to fetch user info")
                return jsonify({"error": "Failed to fetch user info"}), 500
            
            profile = info['user']['profile']
            email = profile.get('email')
            name = profile.get('real_name') or profile.get('display_name') or 'Unknown'

            user = User(slack_user_id=slack_user_id, email=email, name=name)
            db.session.add(user)
            db.session.commit()
    except Exception as e:
        logger.error("Internal Server Error")
        return jsonify({"error": "Internal Server Error"}), 500

    return jsonify({})
