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
    else:
        data = request.args.post
        tree = xml.etree.ElementTree.fromstring(data)
        root = tree.getroot()
        MsgType = root.find('MsgType').text

        ToUserName = root.find('ToUserName').text
        FromUserName = root.find('FromUserName').text
        FromUserName = root.find('FromUserName').text
        MsgType = root.find('MsgType').text
        MsgId = root.find('MsgId').text

        tfp = open(config.BASE_DIR + 'log/weixin-'+str(MsgId)+'.log', 'w')
        tfp.write(data)
        tfp.close()

        return make_response(data)
