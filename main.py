import time
import requests
import os
import schedule
import datetime
import plotly.graph_objects as go
import threading
import pandas as pd
from flask import Flask, request, jsonify, render_template
from concurrent import futures
import telebot
import prep
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import random

server = Flask(__name__)

# bot = telebot.TeleBot(os.getenv("TELEGRAMTOKEN"), parse_mode=None)

@server.route('/subscribe/<stock>', methods = ['POST'])
def subscribe(stock):
    config = open('config.txt', 'a')
    config.write(stock)
    config.close()

def transfer():
    with open('config.txt', 'r') as f:
        stocks = f.read().splitlines()

    wr_ = open('templates/transfer.html', "w")
    wr_.write('<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>')

    for stock in stocks:
        prepor = prep.populate(width = 980, height=610, symbol = stock, interval = 120,
                               timezone='Etc/UTC', theme='dark', style = '1', locale = 'en', toolbar_bg='#f1f3f6',
                               enable_publishing = False, allow_symbol_change=True, container_id='tradingview_' + str(random.randrange(100000000)))
        tr = prepor.get_chart()
        wr_.write(tr)

    wr_.close()

    attachment = open('templates/transfer.html', "rb")

    fromaddr = "//"
    toaddr = ["//"]

    msg = MIMEMultipart('alternative')


    msg['From'] = fromaddr
    # msg['To'] = toaddr
    msg['Subject'] = "Stocks"

    html = '"<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><div class="tradingview-widget-container"><div id="tradingview_4245252552"></div><script type="text/javascript">new TradingView.widget({"width": 980,"height": 610,"symbol": "NASDAQ:AAPL","interval": "60","timezone": "Etc/UTC","theme": "dark","style": "1","locale": "ru","toolbar_bg": "#f1f3f6","enable_publishing": false,"allow_symbol_change": true,"container_id": "tradingview_4245252552"});</script></div>"'

    msg.attach(MIMEText(html, 'html'))

    # filename = "stock.html"

    # part = MIMEBase('application', 'octet-stream')
    # part.set_payload((attachment).read())
    # encoders.encode_base64(part)
    # part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "//")
    text = msg.as_string()
    for email in toaddr:
        server.sendmail(fromaddr, email, msg.as_string())
    server.quit()

    attachment.close()
    # os.remove('transfer.html')


schedule.every(1).do(transfer)

def check_transfer():
    while True:
        schedule.run_pending()
        time.sleep(1)

@server.route("/")
def index():
    return render_template("transfer.html")

@server.route("/update")
def update():
    transfer()

if __name__ == "__main__":
    thread = threading.Thread(target=check_transfer)
    thread.start()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))