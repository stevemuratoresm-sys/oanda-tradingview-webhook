import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Hardcoded OANDA Production Credentials
OANDA_API_URL = "https://oanda.com"  # Change to fxpractice if on a demo account
ACCOUNT_ID = "YOUR_ACCOUNT_ID"                      # Paste your real OANDA ID inside the quotes
API_TOKEN = "YOUR_OANDA_API_TOKEN"                 # Paste your real bearer token inside the quotes

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400

    action = data.get("action")   # BUY or SELL
    ticker = data.get("ticker")   # EURUSD, AUDUSD, etc.
    units = data.get("units")     # Base unit volume sizing (1000)
    sl = data.get("sl")           # Midpoint value string passed from chart

    if not action or not ticker or not units:
        return jsonify({"error": "Missing required execution keys"}), 400

    # Ensure action strings match up properly
    action = action.upper()
    if action not in ["BUY", "SELL"]:
        return jsonify({"error": "Invalid action value"}), 400

    try:
        units = int(units)
    except ValueError:
        return jsonify({"error": "Invalid units parameter"}), 400

    # OANDA treats short orders as a negative unit volume value
    if action == "SELL":
        units = -abs(units)

    # Format ticker strings for OANDA format (e.g., EUR_USD)
    if len(ticker) == 6:
        ticker = f"{ticker[:3]}_{ticker[3:]}"

    # Setup the live market order transaction request structure
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    order_payload = {
        "order": {
            "units": str(units),
            "instrument": ticker.upper(),
            "timeInForce": "FOK",
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }

    # Inject your midpoint stop-loss if it was cleanly calculated by the bot
    if sl and sl != "na":
        try:
            sl_price = round(float(sl), 5)
            order_payload["order"]["stopLossOnFill"] = {"price": str(sl_price)}
        except ValueError:
            pass

    # Ship the transaction straight to OANDA's execution server
    try:
        url = f"{OANDA_API_URL}/accounts/{ACCOUNT_ID}/orders"
        response = requests.post(url, json=order_payload, headers=headers, timeout=10)
        return jsonify({"status": "Success", "oanda_response": response.json()}), response.status_code
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
