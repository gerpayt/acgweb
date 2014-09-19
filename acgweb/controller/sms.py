# coding: utf-8
from .template_filter import *
from flask import abort, flash
from acgweb import app, db
from acgweb import config
from urllib import quote_plus
import urllib2


messages = {
    '0': '短信发送成功',
    '30': '密码错误',
    '40': '账号不存在',
    '41': '余额不足',
    '42': '帐号过期',
    '43': 'IP地址限制',
    '50': '内容含有敏感词',
    '51': '手机号码不正确'
}


def send_sms(phone, content):
    print "SMS SEND : %s\n%s : %d" % (phone, content, len(content))
    url = config.SMS_BASE_URL + config.SMS_SEND_URL.format(username=config.SMS_USERNAME, password=config.SMS_PASSWORD, phone=phone, content=quote_plus(str(content)))
    print url
    if 0:
        response = urllib2.urlopen(url)
        rtn = response.read()
    else:
        rtn = '0'
        print rtn
    log_sms(phone, content, rtn)
    if rtn == '0':
        flash({'type': 'success', 'content': '短信发送成功'})
        return True
    else:
        flash({'type': 'danger', 'content': messages[rtn]})
        return messages[rtn]


def log_sms(phone, content, rtn):

    content = content.replace("\n", "\\n")
    log = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\t" + phone + "\t" + rtn + "\n" + content

    try:
        fp = open(config.BASE_DIR + 'log/sms.log', 'a')
    except:
        fp = open(config.BASE_DIR + 'log/sms.log', 'w')

    fp.write("%s\n" % log)
    fp.close()


sms_cover_duty_tmpl = '''你的带班申请成功处理
代班人 %s
值班时间 %s
活动地点 %s
活动内容 %s
'''

sms_approve_apply_tmpl = '''班长批准了值班申请
值班时间 %s
活动地点 %s
活动内容 %s
'''

sms_decline_apply_tmpl = '''班长拒绝了值班申请
值班时间 %s
活动地点 %s
活动内容 %s
'''

sms_decline_duty_tmpl = '''%s 拒绝了排班
值班时间 %s
活动地点 %s
活动内容 %s
'''

sms_activity_modify_tmpl = '''你值班的活动信息发生了变化
值班时间 %s 修改为 %s
活动地点 %s 修改为 %s
活动内容 %s 修改为 %s
'''

sms_activity_cancel_tmpl = '''你值班的活动被取消了
值班时间 %s
活动地点 %s
活动内容 %s
'''

sms_activity_appoint_tmpl = '''班长指派了一个活动
值班时间 %s
活动地点 %s
活动内容 %s
'''
