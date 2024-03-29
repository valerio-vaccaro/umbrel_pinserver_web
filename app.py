#!/usr/bin/env python

import cbor
from flask import Flask
from flask import request
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
PINSERVER_URL_A = os.getenv('PINSERVER_URL_A')
PINSERVER_PORT_A = os.getenv('PINSERVER_PORT_A')
PINSERVER_URL_B = os.getenv('PINSERVER_URL_B')
PINSERVER_PORT_B = os.getenv('PINSERVER_PORT_B')
PINSERVER_CERT = os.getenv('PINSERVER_CERT')

# check keys
with open('/app/'+PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE, 'rb') as f:
    PINSERVER_PUBKEY = f.read().hex()

if PINSERVER_PUBKEY == '0332b360a51923db6506cb3560a7216fe00ba15138f97283219cb12cc956f119df':
    print('Generating new keys')
    private_key, public_key = PINServerECDH.generate_ec_key_pair()

    with open('/app/'+PINServerECDH.STATIC_SERVER_PRIVATE_KEY_FILE, 'wb') as f:
        f.write(private_key)

    with open('/app/'+PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE, 'wb') as f:
        f.write(public_key)

    print(
        f'New private key written to file {PINServerECDH.STATIC_SERVER_PRIVATE_KEY_FILE}')
    print(
        f'New public key written to file {PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE}')

with open(PINServerECDH.STATIC_SERVER_PUBLIC_KEY_FILE, 'rb') as f:
    PINSERVER_PUBKEY = f.read().hex()

print(f'PINSERVER_PUBKEY {PINSERVER_PUBKEY}')

app = Flask(__name__)
qrcode = QRcode(app)


@app.route('/')
def index():
    global PINSERVER_URL_A
    global PINSERVER_PORT_A
    global PINSERVER_URL_B
    global PINSERVER_PORT_B
    global PINSERVER_CERT
    
    urla = request.args.get('urla')
    if urla is None:
        urla = PINSERVER_URL_A
    porta = request.args.get('porta')
    if porta is None:
        porta = PINSERVER_PORT_A
    urlb = request.args.get('urlb')
    if urlb is None:
        urlb = PINSERVER_URL_B
    portb = request.args.get('portb')
    if portb is None:
        portb = PINSERVER_PORT_B
    cert = request.args.get('cert')
    if cert is None:
        cert = PINSERVER_CERT

    if PINSERVER_URL_A == 'notyetset.onion':
        return render_template('error.html')
    else:
        keysno = len(os.listdir('/app/pins'))
        return render_template('index.html', urla=urla, porta=porta, urlb=urlb, portb=portb, pubkey=PINSERVER_PUBKEY, cert=cert, keysno=keysno)


@app.route('/server_public_key.pub')
def send_key():
    return send_from_directory('', 'server_public_key.pub')


@app.route('/statics/<path:path>')
def send_report(path):
    return send_from_directory('statics', path)


@app.route("/qrcode", methods=["GET"])
def get_qrcode():    
    global PINSERVER_URL_A
    global PINSERVER_PORT_A
    global PINSERVER_URL_B
    global PINSERVER_PORT_B
    global PINSERVER_CERT
    
    urla = request.args.get('urla')
    if urla is None:
        urla = PINSERVER_URL_A
    porta = request.args.get('porta')
    if porta is None:
        porta = PINSERVER_PORT_A
    urlb = request.args.get('urlb')
    if urlb is None:
        urlb = PINSERVER_URL_B
    portb = request.args.get('portb')
    if portb is None:
        portb = PINSERVER_PORT_B
    cert = request.args.get('cert')
    if cert is None:
        cert = PINSERVER_CERT

    payload = {
        'method': 'update_pinserver',
        'id': '001',
        'params': {
            'urlA': f'{urla}:{porta}',
            'urlB': f'{urlb}:{portb}',
            'pubkey': bytes.fromhex(PINSERVER_PUBKEY)
        }
    }

    if len(cert) > 0:
        payload['params']['cert'] = bytes.fromhex(cert)

    data = cbor.dumps(payload)
    payload = ur.UR('jade-updps', data)
    encoder = ur_encoder.UREncoder(payload, 1000)
    text = encoder.next_part().upper()
    return send_file(qrcode(text, mode="raw"), mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8095)
