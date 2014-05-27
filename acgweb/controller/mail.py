# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, abort, flash
from acgweb import app, db
import acgweb.const as CONST
from acgweb import config
from acgweb.model.message import Message
import os,md5
import smtplib
from email.mime.text import MIMEText

from threading import Thread

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper


def send_message(touid,fromuid,subject,content,type):
    message = Message()
    message.fromuid = fromuid
    message.touid = touid
    message.subject = subject
    message.content = content
    message.type = type
    message.status = 0
    db.session.add(message)
    db.session.commit()

def send_mail(subject,content,toname,toemail):
    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = "%s<%s>" % (config.SMTP_USERNAME, config.SMTP_USER)
    msg['To'] = "%s<%s>" % (toname, toemail)
    msg['Subject'] = subject
    send_async_email(msg,toemail)

@async
def send_async_email(msg,toemail):
    # send email
    #print config.SMTP_SERVER, config.SMTP_PORT,config.SMTP_USER, config.SMTP_PASSWORD,config.SMTP_USER, config.EMAIL_SALES, msg.as_string()
    s = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
    s.login(config.SMTP_USER, config.SMTP_PASSWORD)
    s.sendmail(config.SMTP_USER, [toemail], msg.as_string())

forgetpassword_tmpl = {'subject':"重置密码",'content':'''
点击下面链接来重置密码 <br />
<a href="%s">%s</a>
'''}

activity_appoint_tmpl = {'subject':"安排值班",'content':'''
排班班长给你指派了一个活动 <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <a href="%s">%s</a>

'''}


activity_cancle_tmpl = {'subject':"活动取消",'content':'''
你值班的活动被取消了<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <a href="%s">%s</a>

'''}

activity_modify_tmpl = {'subject':"活动信息变化",'content':'''
你值班的活动信息发生了变化<br />
活动时间 %s 修改为 %s <br />
活动地点 %s 修改为 %s <br />
活动内容 %s 修改为 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <a href="%s">%s</a>

'''}

approve_apply_tmpl = {'subject':"批准值班申请",'content':'''
排班班长批准了你的值班申请<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <a href="%s">%s</a>
'''}

decline_apply_tmpl = {'subject':"拒绝值班申请",'content':'''
排班班长拒绝了你的值班申请<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <a href="%s">%s</a>
'''}

cover_duty_tmpl = {'subject':"找人代班成功",'content':'''
你的带班申请成功处理<br />
代班人 <a href="%s">%s</a> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <a href="%s">%s</a>
'''}

activity_nearly_begin_tmpl = {'subject':"活动即将开始",'content':'''
还有两个小时活动就要开始，请准时赶往活动场地<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <a href="%s">%s</a>
'''}

