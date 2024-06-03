# routes.py
from flask import request, jsonify

def handle_challenge():
    data = request.json 
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})