# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, abort, flash
from acgweb import app, db
import acgweb.const as CONST
from acgweb import config
from acgweb.model.message import Message
import os,md5,time
import smtplib
import imaplib,email
from pprint import pprint
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
    return message.id

def send_mail(subject,content,toname,toemail,**header):
    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = "%s<%s>" % (config.SMTP_USERNAME, config.SMTP_USER)
    msg['To'] = "%s<%s>" % (toname, toemail)
    msg['Subject'] = subject
    msg['X-ACG-MSGDOMAIN'] = config.MAIL_DOMAIN
    for h,v in header.values:
        msg['X-ACG-'+h.upper()] = str(v)
    send_async_email(msg,toemail)

@async
def send_async_email(msg,toemail):
    # send email
    #print config.SMTP_SERVER, config.SMTP_PORT,config.SMTP_USER, config.SMTP_PASSWORD,config.SMTP_USER, config.EMAIL_SALES, msg.as_string()
    #try:
    s = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
    s.login(config.SMTP_USER, config.SMTP_PASSWORD)
    s.sendmail(config.SMTP_USER, [toemail], msg.as_string())
    s.quit()
    #except Exception as e:
    #    try:
    #        fp = open(config.BASE_DIR+'log/error.log','a')
    #    except:
    #        fp = open(config.BASE_DIR+'log/error.log','w')
    #    fp.write("%s\n"%e)
    #    fp.close()

def get_out_box():
    imaplib.Debug = 4
    con = imaplib.IMAP4_SSL(config.IMAP_SERVER)
    con.login(config.SMTP_USER, config.SMTP_PASSWORD)
    con.select('Sent Messages')
    timestr = '"%s"' % time.strftime("%d-%b-%Y",time.localtime(time.time()-2*86400-8*3600))
    #typ,msgidlist = con.search(None,"HEADER", '"X-ACG-MSGDOMAIN"', '"acg-test"' )
    typ,msgidlist = con.search(None, 'SINCE', timestr )
    msgids = msgidlist[0].split()[-20:]
    msgids.reverse()
    ids = ','.join(msgids)
    typ,msg_data= con.fetch(ids,'(BODY.PEEK[HEADER])')
    mail_list = []
    for response_part in msg_data:
        if isinstance(response_part,tuple):
            msg = email.message_from_string(response_part[1])
            if msg.get('X-ACG-MSGDOMAIN') == config.MAIL_DOMAIN or 1:
                for header in ['subject','from','to','date','x-acg-msgid']:
                    res,ecode=email.Header.decode_header(msg.get(header))[0]
                    msg.set_param(header,res)
                    print '%-8s: %s'%(header.upper(),msg.get_param(header))

                fromusername,fromusermail = email.utils.parseaddr(msg.get_param('from'))
                tousername,tousermail = email.utils.parseaddr(msg.get_param('to'))
                sendtime = int(time.mktime(time.strptime(msg.get("date")[5:-6],'%d %b %Y %H:%M:%S')))
                m = {}
                m['subject'] = msg['subject']
                m['fromusername'] = fromusername
                m['fromusermail'] =fromusermail
                m['tousername'] = tousername
                m['tousermail'] = tousermail
                if msg.has_key('x-acg-msgid'):
                    m['msgid'] = int(msg['x-acg-msgid'])
                m['sendtime'] = sendtime
                mail_list.append(m)
    return mail_list


register_tmpl = {'subject':"[音控组管理系统]注册成功",'content':'''
欢迎您注册音控组管理系统，新注册用户请先完善个人资料和课表。 <br />
系统的使用说明参见 <a href="%s">%s</a> <br />
如果遇到问题，请联系 <a href="%s">%s</a> <br />

'''}

forgetpassword_tmpl = {'subject':"[音控组管理系统]重置密码",'content':'''
点击下面链接来重置密码 <br />
<a href="%s">%s</a>

'''}

activity_appoint_tmpl = {'subject':"[音控组管理系统]安排值班",'content':'''
排班班长给你指派了一个活动 <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <br />
<a href="%s">%s</a> <br />
请于活动开始前一个小时 (%s) 到达活动场地

'''}


activity_cancle_tmpl = {'subject':"[音控组管理系统]活动取消",'content':'''
你值班的活动被取消了<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

activity_modify_tmpl = {'subject':"[音控组管理系统]活动信息变化",'content':'''
你值班的活动信息发生了变化<br />
活动时间 %s 修改为 %s <br />
活动地点 %s 修改为 %s <br />
活动内容 %s 修改为 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

approve_apply_tmpl = {'subject':"[音控组管理系统]批准值班申请",'content':'''
排班班长批准了你的值班申请<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

decline_apply_tmpl = {'subject':"[音控组管理系统]拒绝值班申请",'content':'''
排班班长拒绝了你的值班申请<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

cover_duty_tmpl = {'subject':"[音控组管理系统]找人代班成功",'content':'''
你的带班申请成功处理<br />
代班人 <a href="%s">%s</a> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

activity_nearly_begin_tmpl = {'subject':"[音控组管理系统]活动即将开始",'content':'''
还有两个小时活动就要开始了，请准时赶往活动场地<br />
值班时间 %s <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

activity_mark_endtime_tmpl = {'subject':"[音控组管理系统]标记活动结束时间",'content':'''
你值班的活动已经结束了，请标记活动结束时间<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <br />
<a href="%s">%s</a>

'''}

decline_duty_tmpl = {'subject':"[音控组管理系统]拒绝排班",'content':'''
%s 拒绝了你的排班<br />
原因 %s <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

notice_activity_modify_tmpl = {'subject':"[音控组管理系统]有一个活动信息变化",'content':'''
有一个活动信息发生了变化<br />
活动时间 %s 修改为 %s <br />
活动地点 %s 修改为 %s <br />
活动内容 %s 修改为 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a> <br />
请手动更改活动信息 <br />

'''}

notice_activity_cancle_tmpl = {'subject':"[音控组管理系统]有一个活动已删除",'content':'''
有一个活动已删除<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
<a href="%s">%s</a> <br />
请手动取消这个活动 <br />

'''}

spider_notice_tmpl = {'subject':"[音控组管理系统]自动同步通知",'content':'''
自动同步操作于 %s 进行 <br />
<hr />

'''}
