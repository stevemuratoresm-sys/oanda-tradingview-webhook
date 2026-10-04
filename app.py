from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home(): return "OANDA webhook is running"

@app.route("/webhook", methods=["POST"])
def webhook():
return "Webhook received"
