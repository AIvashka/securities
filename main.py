import time
import os
import schedule
import threading
from flask import Flask, request, jsonify, render_template
import prep
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import random

server = Flask(__name__)


@server.route('/subscribe/<stock>', methods = ['POST'])
def subscribe(stock):
    config = open('config.txt', 'a')
    config.write(stock + '\n')
    config.close()
    transfer()
    return jsonify('OK'), 200

@server.route('/subscribe_email/<email>', methods = ['POST'])
def subscribe_email(email):
    config = open('emails.txt', 'a')
    config.write(email + '\n')
    config.close()
    return jsonify('OK'), 200

@server.route('/force_send')
def force_send():
    send_email()
    return jsonify('OK'), 200

@server.route('/force_transfer')
def force_transfer():
    transfer()
    return jsonify('OK'), 200

def send_email():
    fromaddr = os.getenv("EMAIL_FROM")

    with open('emails.txt', 'r') as f:
        emails = f.read().splitlines()

    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['Subject'] = "Stocks"
    plain = 'Hi, mate https://stocks-digest.herokuapp.com/'
    msg.attach(MIMEText(plain, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, os.getenv('EMAIL_PASS'))
    for email in emails:
        msg['To'] = email
        server.sendmail(fromaddr, email, msg.as_string())
    server.quit()

def transfer():
    with open('config.txt', 'r') as f:
        stocks = f.read().splitlines()
    wr_ = open('templates/transfer.html', "w")
    wr_.write('<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>')
    for stock in stocks:
        prepor = prep.populate(width = 980, height=610, symbol = stock, interval = 60,
                               timezone='Etc/UTC', theme='dark', style = '1', locale = 'en', toolbar_bg='#f1f3f6',
                               enable_publishing = False, allow_symbol_change=True, container_id='tradingview_' + str(random.randrange(100000000)))
        tr = prepor.get_chart()
        wr_.write(tr)
    wr_.close()



schedule.every().day.at("13:00").do(send_email)
schedule.every().day.at("23:00").do(send_email)


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