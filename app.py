#!/usr/bin/env python

import cbor
from flask import Flask
from flask import render_template
from flask import send_file
from flask import send_from_directory
from flask_qrcode import QRcode
import os
import sys
from ur import ur
from ur import ur_encoder


# get info from env variables
PINSERVER_URL = os.getenv('PINSERVER_URL')
PINSERVER_PORT = os.getenv('PINSERVER_PORT')

# check if key exists (/server_private_key.key)
if not os.path.isfile("/server_private_key.key"):
    # generate new key
    os.system("python generate.py")

# if exist retrieve content
PINSERVER_PUBKEY='02d938270777210a18cc77558e4390a7376884c56580bcb87ee3ce0e44691da52f'

app = Flask(__name__)
qrcode = QRcode(app)

@app.route('/')
def index():
    return render_template('index.html', url=PINSERVER_URL, port=PINSERVER_PORT, pubkey=PINSERVER_PUBKEY)
    
@app.route('/statics/<path:path>')
def send_report(path):
    return send_from_directory('statics', path)

@app.route("/qrcode", methods=["GET"])
def get_qrcode():
    data = cbor.dumps({
        'method': 'update_pinserver', 
        'id': '001',
        'params': {
            'urlA': f'{PINSERVER_URL}:{PINSERVER_PORT}',
            'pubkey': bytes.fromhex(PINSERVER_PUBKEY)
        }
    })
    payload = ur.UR('jade-updps', data)
    encoder = ur_encoder.UREncoder(payload, 1000)
    text = encoder.next_part().upper()
    return send_file(qrcode(text, mode="raw"), mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
