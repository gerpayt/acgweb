# coding: utf-8

from flask import render_template, flash, jsonify, abort, make_response, json, request
from acgweb import app, db, config
from acgweb import config
import hashlib


@app.route('/weixinapi/token')
def check_signature():
    signature = request.args.get('signature')
    echostr = request.args.get('echostr')

    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    token = config.WEIXIN_TOKEN

    sig_arr = [token, timestamp, nonce]
    sig_arr.sort()
    sig_str = ''.join(sig_arr)
    sig_str = hashlib.sha1(sig_arr)

    if sig_str == signature:
        print echostr
        return True
    else:
        return False
