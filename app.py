from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

OANDA_TOKEN = os.environ["OANDA_TOKEN"]
OANDA_ACCOUNT_ID = os.environ["OANDA_ACCOUNT_ID"]

OANDA_URL = "https://api-fxpractice.oanda.com/v3"

headers = {
"Authorization": f"Bearer {OANDA_TOKEN}",
"Content-Type": "application/json"
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON received"}), 400

action = data.get("action")
instrument = data.get("instrument")
units = data.get("units")

if action not in ["BUY", "SELL"]:
    return jsonify({"error": "Invalid action"}), 400

try:
units = int(units)
except:
return jsonify({"error": "Invalid units"}), 400

if action == "SELL":
units = -abs(units)
else:
units = abs(units)

order = {
"order": {
"type": "MARKET",
"instrument": instrument,
"units": str(units),
"timeInForce": "FOK",
"positionFill": "DEFAULT"
}
}

response = requests.post(
f"{OANDA_URL}/accounts/{OANDA_ACCOUNT_ID}/orders",
headers=headers,
json=order,
timeout=2
)

return jsonify(response.json()), response.status_code

@app.route("/", methods=["GET"])
def home():
return "OANDA webhook is running"

if __name__ == "__main__":
app.run(
host="0.0.0.0",
port=int(os.environ.get("PORT", 10000))
)
