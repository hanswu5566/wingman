from app.secret import Secret
from authlib.integrations.flask_client import OAuth
from flask import Flask

oauth = OAuth()

def init_oauth(app:Flask):
    oauth.init_app(app=app)
    oauth.register(
        'slack',
        client_id=Secret.SLACK_CLIENT_ID,
        client_secret=Secret.SLACK_CLIENT_SECRET,
        authorize_url='https://slack.com/oauth/v2/authorize',
        authorize_params=None,
        access_token_url='https://slack.com/api/oauth.v2.access',
        access_token_params=None,
        client_kwargs={'scope': 'users:read,app_mentions:read,channels:read,chat:write,commands'},
    )
    oauth.register(
        'clickup',
        client_id=Secret.CLICKUP_CLIENT_ID,
        client_secret=Secret.CLICKUP_CLIENT_SECRET,
        authorize_url='https://api.clickup.com/api/v2/oauth/token',
        authorize_params=None,
        access_token_params=None,
        refresh_token_url=None,
        client_kwargs={'scope': 'team:read'},
    )

