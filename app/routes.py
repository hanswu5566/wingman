# # routes.py
# from flask import request, session,redirect, jsonify,url_for
# from .tasks import handle_slack_event
# from .extensions import celery_instance, slack_bot_client
# from .config import Config
# from .models import user
# from .oauth import oauth
# from .db import db
# from .event_handlers import handle_challenge
# import slack_sdk

# def register_routes(app):
#     # @app.route("/", methods=["GET"])
#     # def index():
#     #     return '''
#     #     <head>
#     #     <link rel="icon" href="/favicon.ico" type="image/x-icon">
#     #     </head>

#     #     <h1>Welcome to the Slack OAuth Demo!</h1>
#     #     <a href="/slack/login">
#     #         <img alt="Sign in with Slack" height="40" width="172"
#     #         src="https://platform.slack-edge.com/img/sign_in_with_slack.png" />
#     #     </a>
#     #     '''

#     # @app.route("/celery/heartbeat", methods=["GET"])
#     # def check_celery():
#     #     i = celery_instance.control.inspect()
#     #     active_workers = i.active()
#     #     if active_workers:
#     #         return jsonify(status="alive"), 200
#     #     else:
#     #         return jsonify(status="dead"), 503

#     @app.route("/slack/events", methods=["POST"])
#     def slack_events():
#         try:
#             data = request.json 
#             handle_challenge()

            

            


#             if "event" in data:
#                 slack_bot_client.chat_postMessage(
#                     channel=data["event"]["channel"], text="[System]: Message received. Please wait..."
#                 )

#                 handle_slack_event.delay(data)

#             return jsonify({})
#         except Exception as e:
#             # Log the exception
#             app.logger.error(f"Error processing Slack event: {e}")
#             return jsonify({"error": "Internal Server Error"}), 500


#     @app.route('/slack/login')
#     def login():
#         return oauth.slack.authorize_redirect(Config.SLACK_REDIRECT_URL)
    
#     @app.route('/slack/logout')
#     def logout():
#         session.pop('slack_token')
#         return redirect(url_for('index'))
    
#     @app.route('/slack/login/authorize')
#     def authorize():
#         try:
#             token = oauth.slack.authorize_access_token()
#             if token['ok']:
#                 access_token = token['access_token']
#                 slack_user_id = token['authed_user']['id']

                
#             else:
#                 app.logger.error(f"OAuth failed: {e}")
#         except Exception as e:
#             app.logger.error(f"Error in OAuth : {e}")
#             return jsonify({"error": "Internal Server Error"}), 500

#         return jsonify({})
    

