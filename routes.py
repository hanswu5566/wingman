# routes.py
from flask import request, session,redirect, jsonify,url_for
from tasks import handle_slack_event
from extensions import celery_instance, bot_client
from config import whitelist_slack_id,slack_redirect_url

def register_routes(app,oauth,db):
    @app.route("/", methods=["GET"])
    def index():
        return '''
        <h1>Welcome to the Slack OAuth Demo!</h1>
        <a href="/slack/login">
            <img alt="Sign in with Slack" height="40" width="172"
            src="https://platform.slack-edge.com/img/sign_in_with_slack.png" />
        </a>
        '''

    @app.route("/celery/heartbeat", methods=["GET"])
    def check_celery():
        i = celery_instance.control.inspect()
        active_workers = i.active()
        if active_workers:
            return jsonify(status="alive"), 200
        else:
            return jsonify(status="dead"), 503

    @app.route("/slack/events", methods=["POST"])
    def slack_events():
        try:
            data = request.json  # Get JSON data from the request
            # Check if this is a challenge request
            if "challenge" in data:
                # Respond with the challenge value to verify this endpoint
                return jsonify({"challenge": data["challenge"]})

            if "event" in data:
                if data["event"]["user"] not in whitelist_slack_id:
                    bot_client.chat_postMessage(
                        channel=data["event"]["channel"],
                        text="Sorry, you're not in the whitelist",
                    )
                else:
                    bot_client.chat_postMessage(
                        channel=data["event"]["channel"], text="OK, please wait...."
                    )

                    handle_slack_event.delay(data)

            return jsonify({})
        except Exception as e:
            # Log the exception
            app.logger.error(f"Error processing Slack event: {e}")
            return jsonify({"error": "Internal Server Error"}), 500


    @app.route('/slack/login')
    def login():
        return oauth.slack.authorize_redirect(slack_redirect_url)
    
    @app.route('/slack/logout')
    def logout():
        session.pop('slack_token')
        return redirect(url_for('index'))
    
    @app.route('/slack/login/authorize')
    def authorize():
        token = oauth.slack.authorize_access_token()
        session['token'] = token
        print(token)
            
        # user = User.query.filter_by(slack_id=slack_id).first()
        # if not user:
        #     user = User(slack_id=slack_id, email=email, name=name)
        #     db.session.add(user)
        #     db.session.commit()

        return jsonify({})