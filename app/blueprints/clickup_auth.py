from flask import Blueprint, jsonify,request, session
from ..models import User
from ..db import db
from ..oauth import oauth
from ..handlers.slack import send_configure_workspace_initial_msg
from ..handlers.clickup import get_authorized_user,get_workspaces,get_spaces
from ..config import Config
from ..logger import logger
from ..secret import Secret
import requests

clickup_auth_bp = Blueprint('click_auth', __name__)

@clickup_auth_bp.route("/login")
def login():
    return oauth.clickup.authorize_redirect(Config.CLICKUP_REDIRECT_URL)

@clickup_auth_bp.route('/login/authorize')
def authorize():
    code = request.args.get('code')
    state = request.args.get('state')
    user_id, channel_id,ts = state.split(',')

    if not code:
        return jsonify({"err": "Authorization code not found", "ECODE": "AUTH_001"}), 400
    
    if not User.get_member(user_id):
        return jsonify({"err": "Member not found", "ECODE": "AUTH_002"}),400

    token_url = 'https://app.clickup.com/api/v2/oauth/token'
    payload = {
        'client_id': Secret.CLICKUP_CLIENT_ID,
        'client_secret': Secret.CLICKUP_CLIENT_SECRET,
        'code': code,
    }

    try:
        res = requests.post(token_url, params=payload)
        if res.ok:
            access_token = res.json()['access_token']
            clickup_user = get_authorized_user(access_token)
            clickup_workspaces = get_workspaces(access_token)

            user = User.query.filter_by(slack_user_id=user_id).first()

            if user and not user.clickup_token:
                user.clickup_token = res.json()['access_token']
                user.clickup_user_id = clickup_user['user']['id']
                user.clickup_user_name = clickup_user['user']['username']

                team = clickup_workspaces['teams'][0]
                spaces = get_spaces(team['id'],access_token)
                user.clickup_workspace = {"id":team['id'],"name":team['name'],'spaces':spaces["spaces"]}

                db.session.commit()
                send_configure_workspace_initial_msg(channel_id,user_id,ts)
                return jsonify({'msg':'You can close the screen and get back to Slack'})
    except Exception as e:
        logger.error(e)
        return jsonify({"Internal Server Error"}), 500
    
    return jsonify({})