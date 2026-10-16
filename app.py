import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# HARD-LOCKED: Points to the secure OANDA Practice/Demo v20 REST gateway
 
OANDA_API_URL = "https://api-fxpractice.oanda.com"

OANDA_TOKEN = os.environ.get("OANDA_TOKEN")
OANDA_ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return "OANDA Webhook Gateway Demo Server is Live and Active!", 200
        
    try:
        data = request.get_json(force=True)
        print("Incoming Root Alert Data Received:", data)
        
        action = data.get("action", "").lower()
        ticker = data.get("ticker", "").replace("/", "_").upper()
        units_raw = data.get("units", "1000")
        
        try:
            units = int(float(units_raw))
        except:
            units = 1000
            
        market_side = "BUY" if "buy" in action or "long" in action else "SELL"
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
        
        headers = {
            "Authorization": f"Bearer {OANDA_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        endpoint = f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders"
        response = requests.post(endpoint, json=order_payload, headers=headers)
        print("OANDA Broker Response Status:", response.status_code)
        
        if "application/json" in response.headers.get("Content-Type", ""):
            broker_data = response.json()
            return jsonify({"status": "success", "broker_response": broker_data}), 200
        else:
            print("CRITICAL ERROR: OANDA Demo Server returned a non-JSON page.")
            return jsonify({"status": "error", "message": "Non-JSON response from OANDA Demo", "raw": response.text[:100]}), 200
        
    except Exception as e:
        print("Fatal Webhook Engine Exception caught:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        print("Incoming Webhook Alert Data Received:", data)
        
        action = data.get("action", "").lower()
        ticker = data.get("ticker", "").replace("/", "_").upper()
        units_raw = data.get("units", "1000")
        
        try:
            units = int(float(units_raw))
        except:
            units = 1000
            
        market_side = "BUY" if "buy" in action or "long" in action else "SELL"
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
        
        headers = {
            "Authorization": f"Bearer {OANDA_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        endpoint = f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders"
        response = requests.post(endpoint, json=order_payload, headers=headers)
        print("OANDA Broker Response Status:", response.status_code)
        
        if "application/json" in response.headers.get("Content-Type", ""):
            broker_data = response.json()
            return jsonify({"status": "success", "broker_response": broker_data}), 200
        else:
            print("CRITICAL ERROR: OANDA Demo Server returned a non-JSON page.")
            return jsonify({"status": "error", "message": "Non-JSON response from OANDA Demo", "raw": response.text[:100]}), 200
        
    except Exception as e:
        print("Fatal Webhook Engine Exception caught:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 200
