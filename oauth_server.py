from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

app = Flask(__name__)

@app.route("/")
def home():
    return "OAuth Server is running!"

@app.route("/oauth/callback", methods=["GET"])
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization code is missing!"}), 400

    token_url = "https://zoom.us/oauth/token"
    headers = {
        "Authorization": f"Basic {CLIENT_ID}:{CLIENT_SECRET}"
    }
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    try:
        response = requests.post(token_url, headers=headers, data=payload)
        response_data = response.json()
        if response.status_code == 200:
            return jsonify(response_data)
        else:
            return jsonify(response_data), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
