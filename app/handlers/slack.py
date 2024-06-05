from flask import jsonify

def handle_challenge(data):
    if "challenge" in data:
        # Respond with the challenge value to verify this endpoint
        return jsonify({"challenge": data["challenge"]})
    


def handle_onboarding(data):
    return jsonify({})