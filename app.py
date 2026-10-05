from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

OANDA_URL = "https://api-fxpractice.oanda.com/v3"


@app.route("/")
def home():
    return "OANDA webhook is running"


@app.route("/webhook", methods=["POST"])
def webhook():
    token = os.environ.get("OANDA_TOKEN")
    account_id = os.environ.get("OANDA_ACCOUNT_ID")

    if not token or not account_id:
        return jsonify({"error": "OANDA credentials missing"}), 500

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

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"{OANDA_URL}/accounts/{account_id}/orders",
        headers=headers,
        json=order,
        timeout=10
    )

    return jsonify(response.json()), response.status_code
