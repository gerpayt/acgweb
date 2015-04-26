# coding: utf-8

from flask import abort, make_response, request
from acgweb import app, config
import time
import hashlib
import xml.etree.ElementTree


@app.route('/weixinapi', methods=['GET', 'POST'])
def weixinapi():
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    token = config.WEIXIN_TOKEN

    signature = request.args.get('signature')
    echostr = request.args.get('echostr')

    sig_arr = [token, timestamp, nonce]
    sig_arr.sort()
    sig_str = ''.join(sig_arr)

    sha1 = hashlib.sha1()
    sha1.update(sig_str)

    if sha1.hexdigest() == signature:
        if request.method == 'GET' and request.args.get('echostr'):
            return make_response(echostr)
        elif request.method == 'POST':
            data = request.data
            tree = xml.etree.ElementTree.fromstring(data)
            msg_type = tree.find('MsgType').text

            to_user_name = tree.find('ToUserName').text
            from_user_name = tree.find('FromUserName').text
            msg_id = tree.find('MsgId').text
            receive_content = tree.find('Content').text

            text_tpl = """<xml>
                            <ToUserName><![CDATA[%s]]></ToUserName>
                            <FromUserName><![CDATA[%s]]></FromUserName>
                            <CreateTime>%s</CreateTime>
                            <MsgType><![CDATA[%s]]></MsgType>
                            <Content><![CDATA[%s]]></Content>
                            <FuncFlag>0</FuncFlag>
                            </xml>"""
            msg_type = "text"
            reply_content = "感谢您的关注！"
            time_str = str(int(time.time))
            result_str = text_tpl % (from_user_name, to_user_name, time_str, msg_type, reply_content)

            tfp = open(config.BASE_DIR + 'log/weixin.log', 'a')
            tfp.write('%s\t%s\n%s\n%s\n\n' % (time_str, msg_id, receive_content, reply_content))
            tfp.close()

            return make_response(result_str)
    else:
        abort(403)