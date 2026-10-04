from flask import Flask, request
import os
import requests

app = Flask(__name__)

@app.route("/")
def home(): return "OANDA webhook is running"

@app.route("/webhook", methods=["POST"])
def webhook():
token = os.environ.get("OANDA_TOKEN")
account_id = os.environ.get("OANDA_ACCOUNT_ID")

if not token or not account_id:
return "OANDA credentials missing", 500

return "Webhook ready"
