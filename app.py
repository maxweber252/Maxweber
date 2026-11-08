from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

# Config
try:
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except:
    CONFIG = {"bot_name": "Marie", "prefix": "+", "owner_name": "Maxweber"}

BOT_NAME = CONFIG.get("bot_name", "Marie")
PREFIX = CONFIG.get("prefix", "+")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "royaume123")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "")

@app.route("/", methods=["GET"])
def home():
    return f"{BOT_NAME} est en ligne !", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Token invalide", 403

    if request.method == "POST":
        data = request.get_json()
        print(data)
        return "OK", 200

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
