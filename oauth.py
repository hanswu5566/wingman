from secret import slack_client_id,slack_client_secret
from authlib.integrations.flask_client import OAuth
from flask import Flask

oauth = OAuth()

def init_oauth(app:Flask):

    oauth.init_app(app=app)
    oauth.register(
        'slack',
        client_id=slack_client_id,
        client_secret=slack_client_secret,
        authorize_url='https://slack.com/oauth/v2/authorize',
        authorize_params=None,
        access_token_url='https://slack.com/api/oauth.v2.access',
        access_token_params=None,
        client_kwargs={'scope': 'users:read,users:read.email,app_mentions:read,channels:read,chat:write'},
    )

