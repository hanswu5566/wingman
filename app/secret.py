import os

class Secret:
    DIFY_TOKEN = os.getenv('dify_token')
    BOT_TOKEN = os.getenv('bot_token')

    SLACK_CLIENT_ID = os.getenv('slack_client_id')
    SLACK_CLIENT_SECRET = os.getenv('slack_client_secret')

    CLICKUP_CLIENT_ID = os.getenv('clickup_client_id')
    CLICKUP_CLIENT_SECRET = os.getenv('clickup_client_secret')

    bot_slack_id = "U028NRCSKJM"