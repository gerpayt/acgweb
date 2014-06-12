# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, abort, flash
from acgweb import app, db
from acgweb.model.message import Message
from acgweb.model.member import Member

import acgweb.const as CONST
from acgweb import config
import template_filter
from decorated_function import *
import time


@app.route('/mymessage-p<int:pagenum>')
@app.route('/mymessage')
@login_required
def mymessage(pagenum=1):
    """Page: all activitylist"""
    message_count = Message.query.filter(Message.touid==session[u'uid']).count()
    message_list = Message.query.filter(Message.touid==session[u'uid']).order_by('sendtime DESC').\
        limit(CONST.message_per_page).offset(CONST.message_per_page*(pagenum-1))
    return render_template('message/messagelist.html',
        message_list=message_list,
        page_count=(message_count-1)/CONST.message_per_page+1,page_current=pagenum)

@app.route('/messagemanage-p<int:pagenum>')
@app.route('/messagemanage')
@login_required
def messagemanage(pagenum=1):
    """Page: all activitylist"""
    message_count = Message.query.count()
    message_list = Message.query.order_by('sendtime DESC').limit(CONST.message_per_page).offset(CONST.message_per_page*(pagenum-1))
    return render_template('message/messagemanage.html',
        message_list=message_list,
        page_count=(message_count-1)/CONST.message_per_page+1,page_current=pagenum)

'''

@app.route('/mymessage-<member_uid>')
@app.route('/mymessage')
@login_required
def mymessage(member_uid=''):
    """Page: all activitylist"""
    #sql = "select max(sendtime) as max_send_time, touid as conv_id, fromuid, touid, subject from message where fromuid = '%s' group by touid union" \
    #      " select max(sendtime) as max_send_time, fromuid as conv_id, fromuid, touid, subject from message where touid = '%s' group by fromuid " % (session[u'uid'],session[u'uid'])
    #print sql
    #res = db.session.execute(sql)
    #conv_list = []
    #conv_dict = {}
    #for i,r in enumerate(res):
    #    if not conv_dict.has_key(r[1]):
    #        conv_dict[r[1]]=1
    #conversation_count = Message.query.filter(or_(Message.touid==session[u'uid'],Message.fromuid==session[u'uid']))group.count()
    #if not member_uid:
    #message_list_fromme = Message.query.select(),filter(Message.fromuid==session[u'uid']).group_by(Message.touid).all()
    #message_list_tome = Message.query.filter(Message.touid==session[u'uid']).group_by(Message.fromuid).all()
    #conv_list = []
    #for m in message_list_fromme:
    #    o={}
    message_count = Message.query.filter(Message.touid==session[u'uid']).count()
    message_list = Message.query.filter(Message.touid==session[u'uid']).all()
    return render_template('message/mymessage.html',
        message_list=message_list)
'''

@app.route('/mymessagedetail-<int:message_id>')
@login_required
def mymessagedetail(message_id=0):
    message = Message.query.get_or_404(message_id)
    if session['uid'] != message.touid and not session.get('is_arra_monitor'):
        abort(403)
    if session['uid'] == message.touid and not message.readtime:
        message.update_readtime()
        db.session.add(message)
        db.session.commit()
    return render_template('message/messagedetail.html',
        message=message)


@app.route('/mymessagesend', methods=['GET', 'POST'])
@login_required
def mymessagesend():

    if request.method == 'POST':
        sendto = request.form.getlist('sendto')
        subject = request.form['subject']
        content = request.form['content']
        for uid in sendto:
            message = Message()
            message.fromuid = session[u'uid']
            message.touid = uid
            message.subject = subject
            message.content = content
            message.type = 9
            message.status = 0
            db.session.add(message)
        db.session.commit()
        flash({'type':'success', 'content':'发送成功！'})

        return redirect(url_for('mymessage'))
    else:
        member = Member.query.get_or_404(session['uid'])
        if member.uid != session[u'uid']:
            abort(403)
        form = MemberForm(obj=member)

        return render_template('message/messagesend.html', form=form)

