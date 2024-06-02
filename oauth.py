from secret import slack_client_id,slack_client_secret
from authlib.integrations.flask_client import OAuth


def init_oauth(app):

    oauth = OAuth(app)
    oauth.register(
        'slack',
        client_id=slack_client_id,
        client_secret=slack_client_secret,
        authorize_url='https://slack.com/oauth/v2/authorize',
        authorize_params=None,
        access_token_url='https://slack.com/api/oauth.v2.access',
        access_token_params=None,
        client_kwargs={'scope': 'users:read users:read.email'},
    )

    return oauth

