from flask import Blueprint, jsonify,request, session, redirect, url_for
from ..models import User
from ..db import db
from ..oauth import oauth
from slack_sdk import WebClient
from ..config import Config
from ..logger import logger
from ..secret import Secret
import os
import requests

clickup_auth_bp = Blueprint('click_auth', __name__)

@clickup_auth_bp.route("/login")
def login():
    return oauth.clickup.authorize_redirect(Config.CLICKUP_REDIRECT_URL)

@clickup_auth_bp.route('/login/authorize')
def authorize():
    code = request.args.get('code')
    if not code:
        return jsonify({"err": "Authorization code not found", "ECODE": "AUTH_001"}), 400
    
    token_url = 'https://app.clickup.com/api/v2/oauth/token'
    payload = {
        'client_id': Secret.CLICKUP_CLIENT_ID,
        'client_secret': Secret.CLICKUP_CLIENT_SECRET,
        'code': code,
    }

    try:
        res = requests.post(token_url, params=payload)
        if res.ok:
            session['token'] = res.json()['access_token']


    except Exception as e:
        logger.error(e)
        return jsonify({"Internal Server Error"}), 500
    
    return jsonify({})