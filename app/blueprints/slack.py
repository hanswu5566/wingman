from flask import Blueprint, request, jsonify, redirect, url_for
from ..handlers.slack import handle_challenge 
from ..models.user import User
slack_bp = Blueprint('slack', __name__)

@slack_bp.route("/events", methods=["POST"])
def slack_events():
    data = request.json
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})
    
    if "event" in data:
        
        event = data['event']
        user_id = event['user']
        channel = event['channel']
        text = event['text']

        if not User.is_member(user_id):
             # 不是會員
             # 告訴他這東西是幹嘛的，會用到他什麼資訊
             # 給他選擇 1. 註冊並登入 

        else:
            print(123213)
            # 是會員，直接處理他的command



        
    
    return jsonify({})