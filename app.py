import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Retrieve secure tokens from Render environment variables
OANDA_API_URL = "https://oanda.com" # Practice Sandbox Environment URL
OANDA_TOKEN = os.environ.get("OANDA_TOKEN")
OANDA_ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Incoming Alert Data Received:", data)
        
        # 1. Extract and sanitize incoming message fields safely
        action = data.get("action", "").lower()
        ticker = data.get("ticker", "").replace("/", "_").upper()
        units_raw = data.get("units", "1000")
        
        # Enforce clean standard unit numeric formats
        try:
            units = int(float(units_raw))
        except:
            units = 1000
            
        # 2. Build the precise OANDA API execution block
        market_side = "BUY" if "buy" in action or "long" in action else "SELL"
        
        # Calculate proper directional signing requirements for OANDA REST API
        if market_side == "SELL" and units > 0:
            units = -units
            
        order_payload = {
            "order": {
                "units": str(units),
                "instrument": ticker,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }
        
        # 3. Securely push transaction downstream to your OANDA ledger
        headers = {
            "Authorization": f"Bearer {OANDA_TOKEN}",
            "Content-Type": "application/json"
        }
        
        endpoint = f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders"
        response = requests.post(endpoint, json=order_payload, headers=headers)
        print("OANDA Broker Response Status:", response.status_code, response.text)
        
        return jsonify({"status": "success", "broker_response": response.json()}), 200
        
    except Exception as e:
        print("Fatal Webhook Engine Exception caught:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 200 # Forces a 200 to clear the TV log panels
