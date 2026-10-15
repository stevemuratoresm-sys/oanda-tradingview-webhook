```python
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# OANDA DEMO / PRACTICE API
OANDA_API_URL = "https://api-fxpractice.oanda.com"
OANDA_TOKEN = os.environ.get("OANDA_TOKEN")
OANDA_ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")


def send_order(data):
    print("Incoming Alert Data:", data)

    if not OANDA_TOKEN or not OANDA_ACCOUNT_ID:
        print("ERROR: Missing OANDA_TOKEN or OANDA_ACCOUNT_ID")
        return jsonify({
            "status": "error",
            "message": "OANDA environment variables are missing"
        }), 500

    # Accept either instrument or ticker
    action = str(data.get("action", "")).strip().lower()
    instrument = str(
        data.get("instrument", data.get("ticker", ""))
    ).strip().upper().replace("/", "_")

    if not instrument:
        return jsonify({
            "status": "error",
            "message": "Missing instrument or ticker"
        }), 400

    if action not in ("buy", "sell", "long", "short"):
        return jsonify({
            "status": "error",
            "message": "Invalid or missing action",
            "received_action": action
        }), 400

    # Units default to 1000; BUY positive, SELL negative
    try:
        units = abs(int(float(data.get("units", 1000))))
    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "Invalid units"
        }), 400

    if units == 0:
        return jsonify({
            "status": "error",
            "message": "Units must not be zero"
        }), 400

    if action in ("sell", "short"):
        units = -units

    order_payload = {
        "order": {
            "units": str(units),
            "instrument": instrument,
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }

    headers = {
        "Authorization": f"Bearer {OANDA_TOKEN}",
        "Content-Type": "application/json"
    }

    endpoint = (
        f"{OANDA_API_URL}/v3/accounts/"
        f"{OANDA_ACCOUNT_ID}/orders"
    )

    try:
        response = requests.post(
            endpoint,
            json=order_payload,
            headers=headers,
            timeout=15
        )

        print("OANDA HTTP Status:", response.status_code)
        print("OANDA Response:", response.text[:3000])

        try:
            broker_data = response.json()
        except ValueError:
            broker_data = {"raw_response": response.text[:1000]}

        if response.ok:
            return jsonify({
                "status": "submitted",
                "oanda_http_status": response.status_code,
                "broker_response": broker_data
            }), 200

        return jsonify({
            "status": "rejected",
            "oanda_http_status": response.status_code,
            "broker_response": broker_data
        }), 502

    except requests.RequestException as e:
        print("OANDA Connection Error:", str(e))
        return jsonify({
            "status": "error",
            "message": "Could not connect to OANDA",
            "details": str(e)
        }), 502


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return "OANDA Demo Webhook Gateway is running.", 200

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request must contain a valid JSON object"
        }), 400

    return send_order(data)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request must contain a valid JSON object"
        }), 400

    return send_order(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
```
