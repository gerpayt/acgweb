# coding: utf-8
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from threading import Thread
import md5

from flask import abort
from acgweb import config
from acgweb.model.message import Message
from decorated_function import *
from template_filter import *


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
    msg['Subject'] = "[%s]%s" % (config.SITE_TITLE, subject)
    msg['X-ACG-MSGDOMAIN'] = config.MAIL_DOMAIN
    for h,v in header.items():
        msg['X-ACG-'+h.upper()] = str(v)
    send_async_email(msg,toemail)


#@async
def send_async_email(msg,toemail):
    now = int(time.time())
    nowstr = timeformat_filter(now, "%Y-%m-%d_%H:%M:%S")
    key = md5.new()
    key.update(msg.as_string())
    hash = key.hexdigest()
    fp = open(config.BASE_DIR+'cache/mail_%s_%s.log'%(nowstr,hash),'w')
    fp.write(msg.as_string())
    fp.close()

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
    #imaplib.Debug = 4
    con = imaplib.IMAP4_SSL(config.IMAP_SERVER)
    con.login(config.SMTP_USER, config.SMTP_PASSWORD)
    con.select('Sent Messages')
    timestr = '"%s"' % time.strftime("%d-%b-%Y",time.localtime(time.time()-2*86400-8*3600))
    #typ,msgidlist = con.search(None,"HEADER", '"X-ACG-MSGDOMAIN"', '"acg-test"' )
    typ,msgidlist = con.search(None, 'SINCE', timestr )
    msgids = msgidlist[0].split()[-50:]
    msgids.reverse()
    ids = ','.join(msgids)
    typ,msg_data= con.fetch(ids,'(BODY.PEEK[HEADER])')
    mail_list = []
    for response_part in msg_data:
        if isinstance(response_part,tuple):
            msg = email.message_from_string(response_part[1])
            if msg.get('X-ACG-MSGDOMAIN') == config.MAIL_DOMAIN:
                for header in ['subject','from','to','date','x-acg-msgid']:
                    res,ecode=email.Header.decode_header(msg.get(header))[0]
                    msg.set_param(header,res)
                    #print '%-8s: %s'%(header.upper(),msg.get_param(header))

                fromusername,fromusermail = email.utils.parseaddr(msg.get_param('from'))
                tousername,tousermail = email.utils.parseaddr(msg.get_param('to'))
                sendtime = int(time.mktime(time.strptime(msg.get("date")[5:-6],'%d %b %Y %H:%M:%S')))
                m = {}
                m['subject'] = msg['subject']
                m['fromusername'] = fromusername
                m['fromusermail'] =fromusermail
                m['tousername'] = tousername
                m['tousermail'] = tousermail
                if msg.get('X-ACG-MSGID'):
                    m['msgid'] = int(msg['X-ACG-MSGID'])
                if msg.get('X-ACG-TOUID'):
                    m['touid'] = msg['X-ACG-TOUID']
                m['sendtime'] = sendtime
                mail_list.append(m)
                #print m
    return mail_list


@app.route("/message_sendmail-<int:message_id>")
@login_required
def message_sendmail(message_id):
    if not session.get('is_arra_monitor'):
        abort(403)
    message = Message.query.get_or_404(message_id)
    send_mail(message.subject,message.content,message.tomember.name,message.tomember.email)
    return redirect(url_for('mymessagedetail', message_id=message_id))


register_tmpl = {'subject':"注册成功",'content':'''
欢迎您注册音控组管理系统，新注册用户请先完善个人资料和课表。 <br />
系统的使用说明参见 <a href="%s">%s</a> <br />
如果遇到问题，请联系 <a href="%s">%s</a> <br />

'''}

forgetpassword_tmpl = {'subject':"重置密码",'content':'''
点击下面链接来重置密码 <br />
<a href="%s">%s</a>

'''}

activity_appoint_tmpl = {'subject':"安排值班",'content':'''
排班班长给你指派了一个活动 <br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <br />
<a href="%s">%s</a> <br />

'''}


activity_cancle_tmpl = {'subject':"活动取消",'content':'''
你值班的活动被取消了<br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

activity_modify_tmpl = {'subject':"活动信息变化",'content':'''
你值班的活动信息发生了变化<br />
<strong>值班时间 %s 修改为 %s </strong> <br />
活动时间 %s 修改为 %s <br />
活动地点 %s 修改为 %s <br />
活动内容 %s 修改为 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

approve_apply_tmpl = {'subject':"批准值班申请",'content':'''
排班班长批准了你的值班申请<br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

decline_apply_tmpl = {'subject':"拒绝值班申请",'content':'''
排班班长拒绝了你的值班申请<br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

cover_duty_tmpl = {'subject':"找人代班成功",'content':'''
你的带班申请成功处理<br />
代班人 <a href="%s">%s</a> <br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

activity_nearly_begin_tmpl = {'subject':"活动即将开始",'content':'''
距离值班时间还有一个小时，请准时赶往活动场地<br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

activity_mark_endtime_tmpl = {'subject':"标记活动结束时间",'content':'''
你值班的活动已经结束了，请标记活动结束时间<br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接来完成操作 <br />
<a href="%s">%s</a>

'''}

decline_duty_tmpl = {'subject':"拒绝排班",'content':'''
%s 拒绝了你的排班<br />
原因 %s <br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
活动备注 %s <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a>

'''}

notice_activity_modify_tmpl = {'subject':"有一个活动信息变化",'content':'''
有一个活动信息发生了变化<br />
活动时间 %s 修改为 %s <br />
活动地点 %s 修改为 %s <br />
活动内容 ‘%s’ 修改为 ‘%s’ <br />
活动备注 ‘%s’ 修改为 ‘%s’ <br />
请点击这个链接查看详细内容 <br />
<a href="%s">%s</a> <br />
请手动更改活动信息 <br />

'''}

notice_activity_cancle_tmpl = {'subject':"有一个活动已删除",'content':'''
有一个活动已删除<br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
<a href="%s">%s</a> <br />
请手动取消这个活动 <br />

'''}

spider_notice_tmpl = {'subject':"自动同步通知",'content':'''
自动同步操作于 %s 进行 <br />
<hr />

'''}

todo_duty_tmpl = {'subject':"近期未完成的操作",'content':'''
音控员 <a href="%s">%s</a> <br />
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
<a href="%s">%s</a> <br />
任务状态 %s <br />
请及时完成相关操作。 <br />

'''}

todo_activity_tmpl = {'subject':"近期未完成的操作",'content':'''
<strong>值班时间 %s </strong> <br />
活动时间 %s <br />
活动地点 %s <br />
活动内容 %s <br />
<a href="%s">%s</a> <br />
活动没有安排足够的音控员，请继续安排。 <br />

'''}

todo_notice_tmpl = {'subject':"近期未完成的操作",'content':'''
最近未完成的操作 <br />
<hr />

'''}
