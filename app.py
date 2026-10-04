from flask import Flask
import os

app = Flask(__name__)

OANDA_TOKEN = os.environ["OANDA_TOKEN"]
OANDA_ACCOUNT_ID = os.environ["OANDA_ACCOUNT_ID"]

@app.route("/")
def home(): return "OANDA webhook is running"
