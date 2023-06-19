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

from blind_pin_server.server import PINServerECDH

# get info from env variables
PINSERVER_URL = os.getenv('PINSERVER_URL')
PINSERVER_PORT = os.getenv('PINSERVER_PORT')

# check keys
with open('/app/'+PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE, 'rb') as f:
    PINSERVER_PUBKEY = f.read().hex()

if PINSERVER_PUBKEY == '0332b360a51923db6506cb3560a7216fe00ba15138f97283219cb12cc956f119df':
    print('Generating new keys')
    # os.remove('/app/'+PINServerECDH.STATIC_SERVER_PRIVATE_KEY_FILE)
    # os.remove('/app/'+PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE)
    # PINServerECDH.generate_server_key_pair()
    """private_key, public_key = PINServerECDH.generate_ec_key_pair()

    with open('/app/'+PINServerECDH.STATIC_SERVER_PRIVATE_KEY_FILE, 'wb') as f:
        f.write(private_key)

    with open('/app/'+PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE, 'wb') as f:
        f.write(public_key)

    print(f'New private key written to file {PINServerECDH.STATIC_SERVER_PRIVATE_KEY_FILE}')
    print(f'New public key written to file {PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE}')"""

with open(PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE, 'rb') as f:
    PINSERVER_PUBKEY = f.read().hex()
print(f'PINSERVER_PUBKEY {PINSERVER_PUBKEY}')

app = Flask(__name__)
qrcode = QRcode(app)

@app.route('/update')
def update():
    private_key, public_key = PINServerECDH.generate_ec_key_pair()

    with open('/app/'+PINServerECDH.STATIC_SERVER_PRIVATE_KEY_FILE, 'wb') as f:
        f.write(private_key)

    with open('/app/'+PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE, 'wb') as f:
        f.write(public_key)

    print(f'New private key written to file {PINServerECDH.STATIC_SERVER_PRIVATE_KEY_FILE}')
    print(f'New public key written to file {PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE}')

@app.route('/')
def index():
    if PINSERVER_PORT==None:
        return render_template('error.html')
    else:
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
