# coding: utf-8
from .template_filter import *
from flask import abort, flash
from acgweb import app, db
from acgweb import config
from urllib import quote_plus
import urllib2


messages = {
    '0': '短信发送成功',
    '30': '短信接口密码错误',
    '40': '短信接口账号不存在',
    '41': '短信接口余额不足',
    '42': '短信接口帐号过期',
    '43': '短信接口IP地址限制',
    '50': '短信接口内容含有敏感词',
    '51': '短信接口手机号码不正确',
    '99': '短信接口网络连接超时'
}


def send_sms(phone, content):
    #print "SMS SEND : %s\n%s : %d" % (phone, content, len(content))
    url = config.SMS_BASE_URL + config.SMS_SEND_URL.format(username=config.SMS_USERNAME, password=config.SMS_PASSWORD, phone=phone, content=quote_plus(str(content)))
    #print url
    if 1:
        try:
            response = urllib2.urlopen(url, timeout=5)
            rtn = response.read()
        except urllib2.URLError:
            rtn = '99'
    else:
        rtn = '0'
    #print rtn
    log_sms(phone, content, rtn)
    if rtn == '0':
        flash({'type': 'success', 'content': '短信发送成功'})
        return True
    else:
        flash({'type': 'danger', 'content': messages[rtn]})
        return messages[rtn]


def log_sms(phone, content, rtn):

    content = content.replace("\n", "\\n")
    log = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\t" + phone + "\t" + rtn + "\t" + content

    try:
        fp = open(config.BASE_DIR + 'log/sms.log', 'a')
    except:
        fp = open(config.BASE_DIR + 'log/sms.log', 'w')

    fp.write("%s\n" % log)
    fp.close()


def query_sms():
    url = config.SMS_BASE_URL + config.SMS_QUERY_URL.format(username=config.SMS_USERNAME, password=config.SMS_PASSWORD)
    #print url
    try:
        response = urllib2.urlopen(url, timeout=5)
        rtn = response.read()
    except urllib2.URLError:
        rtn = ''
    send, rest = '-', '-'
    if rtn.startswith("0\n"):
        (send, rest) = rtn[2:].split(',')
    #print send, rest
    return send, rest


sms_cover_duty_tmpl = '''【音控组】代班成功 %s 帮你代了班 %s [%s] 活动:%s'''

sms_approve_apply_tmpl = '''【音控组】班长批准值班 %s [%s] 活动:%s'''

sms_decline_apply_tmpl = '''【音控组】班长拒绝值班 %s [%s] 活动:%s'''

sms_decline_duty_tmpl = '''【音控组】%s 拒绝排班 %s [%s] 活动:%s'''

sms_activity_modify_tmpl = '''【音控组】活动信息变化 时间:%s 地点:%s 活动:%s'''

sms_activity_cancel_tmpl = '''【音控组】活动取消 %s [%s] 活动:%s'''

sms_activity_appoint_tmpl = '''【音控组】班长排班 %s [%s] 活动:%s'''

sms_activity_nearly_begin_tmpl = '''【音控组】活动即将开始 %s [%s] 活动:%s '''

sms_activity_mark_endtime_tmpl = '''【音控组】标记活动结束时间 活动:%s '''

sms_forgetpassword_tmpl = '''【音控组】重置密码 验证码为 %s 请在APP中填写此验证码来继续操作。'''
