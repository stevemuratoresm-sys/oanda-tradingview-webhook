import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Retrieve secure tokens from your Render environment parameters
OANDA_API_URL = "https://oanda.com" 
OANDA_TOKEN = os.environ.get("OANDA_TOKEN")
OANDA_ACCOUNT_ID = os.environ.get("OANDA_ACCOUNT_ID")

# PERMANENT ERROR FIX: Added 'POST' to allow root URL webhook transmissions seamlessly
@app.route('/', methods=['GET', 'POST'])
def home():
    # If it's a routine browser check, show the active confirmation message
    if request.method == 'GET':
        return "OANDA Webhook Gateway Server is Live and Active!", 200
        
    # If it's a live breakout execution alert from TradingView, process the order instantly
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
            "Content-Type": "application/json"
        }
        
        endpoint = f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders"
        response = requests.post(endpoint, json=order_payload, headers=headers)
        print("OANDA Broker Response Status:", response.status_code, response.text)
        
        return jsonify({"status": "success", "broker_response": response.json()}), 200
        
    except Exception as e:
        print("Fatal Webhook Engine Exception caught:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 200

# Secondary backup route path tracking
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
            "Content-Type": "application/json"
        }
        
        endpoint = f"{OANDA_API_URL}/v3/accounts/{OANDA_ACCOUNT_ID}/orders"
        response = requests.post(endpoint, json=order_payload, headers=headers)
        print("OANDA Broker Response Status:", response.status_code, response.text)
        
        return jsonify({"status": "success", "broker_response": response.json()}), 200
        
    except Exception as e:
        print("Fatal Webhook Engine Exception caught:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 200
