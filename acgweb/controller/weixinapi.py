# coding: utf-8

from flask import render_template, flash, jsonify, abort, make_response, json, request
from acgweb import app, db, config
from acgweb import config
import hashlib
import xml.etree.ElementTree


@app.route('/weixinapi', methods=['GET', 'POST'])
def weixinapi():
    if request.method == 'GET' and request.args.get('echostr'):
        signature = request.args.get('signature')
        echostr = request.args.get('echostr')

        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        token = config.WEIXIN_TOKEN

        sig_arr = [token, timestamp, nonce]
        sig_arr.sort()
        sig_str = ''.join(sig_arr)

        sha1 = hashlib.sha1()
        sha1.update(sig_str)

        if sha1.hexdigest() == signature:
            return make_response(echostr)
        else:
            abort(403)
    elif request.method == 'POST':
        data = request.data

        tfp = open(config.BASE_DIR + 'log/weixin.log', 'w')
        tfp.write(data)
        tfp.close()

        tree = xml.etree.ElementTree.fromstring(data)
        MsgType = tree.find('MsgType').text

        ToUserName = tree.find('ToUserName').text
        FromUserName = tree.find('FromUserName').text
        FromUserName = tree.find('FromUserName').text
        MsgType = tree.find('MsgType').text
        MsgId = tree.find('MsgId').text

        return make_response(data)
