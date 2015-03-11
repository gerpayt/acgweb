# coding: utf-8
from flask import render_template, json, abort, flash, make_response
from acgweb import app, db
from acgweb.model.message import Message
from acgweb.model.member import Member
from acgweb.form.member import MemberForm

import acgweb.const as CONST
from decorated_function import *


@app.route('/mymessage-p<int:pagenum>')
@app.route('/mymessage')
@login_required
def mymessage(pagenum=1):
    """Page: all activitylist"""
    message_count = Message.query.filter(Message.touid == session[u'uid']).count()
    message_list = Message.query.filter(Message.touid == session[u'uid']).order_by('sendtime DESC').\
        limit(CONST.message_per_page).offset(CONST.message_per_page * (pagenum - 1))
    if viewtype() == 1:
        return render_template('message/messagelist_mobile.html',
        message_list=message_list,
        page_count=(message_count - 1) / CONST.message_per_page + 1, page_current=pagenum)
    else:
        return render_template('message/messagelist.html',
        message_list=message_list,
        page_count=(message_count - 1) / CONST.message_per_page + 1, page_current=pagenum)


@app.route('/api/mymessagelist')
@return_json
def mymessageapi(me):
    pagenum = int(request.args.get('pagenum', 1))
    message_list = Message.query.filter(Message.touid == me.uid).order_by('sendtime DESC').\
        limit(CONST.message_per_page).offset(CONST.message_per_page * (pagenum - 1))
    res = []
    for message in message_list:
        d = {}
        d['id'] = message.id
        d['subject'] = message.subject
        d['sendtime'] = message.sendtime
        d['readtime'] = message.readtime
        d['type'] = message.type
        res.append(d)
    return res


@app.route('/messagemanage-p<int:pagenum>')
@app.route('/messagemanage')
@login_required
def messagemanage(pagenum=1):
    """Page: all activitylist"""
    message_count = Message.query.count()
    message_list = Message.query.order_by('sendtime DESC').limit(CONST.message_per_page).offset(CONST.message_per_page * (pagenum - 1))
    return render_template('message/messagemanage.html',
        message_list=message_list,
        page_count=(message_count - 1) / CONST.message_per_page + 1, page_current=pagenum)

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


@app.route('/mymessage-<int:message_id>')
@login_required
def mymessagedetail(message_id=0):
    message = Message.query.get_or_404(message_id)
    if session['uid'] != message.touid and not session.get('is_arra_monitor'):
        abort(403)
    if session['uid'] == message.touid and not message.readtime:
        message.update_readtime()
        db.session.add(message)
        db.session.commit()
    if viewtype() == 1:
        return render_template('message/messagedetail_mobile.html',
        message=message)
    else:
        return render_template('message/messagedetail.html',
            message=message)


@app.route('/api/mymessagedetail')
@return_json
def messagedetailapi(me):
    message_id = int(request.args.get('message_id', 0))
    message = Message.query.query.filter(Message.id == message_id and Message.touid == me.uid).first()
    if message:
        if me.uid == message.touid and not message.readtime:
            message.update_readtime()
            db.session.add(message)
            db.session.commit()
        res = {}
        res['id'] = message.id
        res['fromuid'] = message.fromuid
        res['touid'] = message.touid
        res['subject'] = message.subject
        res['content'] = message.content
        res['sendtime'] = message.sendtime
        res['readtime'] = message.readtime
        res['type'] = message.type
        res['status'] = message.status
        res['frommember'] = {'name': message.frommember.name, 'mobile': message.frommember.mobile_num}
        res['tomember'] = {'name': message.tomember.name, 'mobile': message.tomember.mobile_num}
    else:
        res = {'error': '404', 'message': '信息不存在。'}
    return res


@app.route('/mymessagesend', methods=['GET', 'POST'])
@login_required
def mymessagesend():

    if request.method == 'POST':
        sendto = request.form.getlist('sendto')
        subject = request.form['subject']
        content = request.form['content']
        if request.form.has_key('mobile'):
            content = content.replace('\n', '<br />\n')
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
        flash({'type': 'success', 'content': '发送成功！'})

        return redirect(url_for('mymessage'))
    else:
        member = Member.query.get_or_404(session['uid'])
        if member.uid != session[u'uid']:
            abort(403)
        form = MemberForm(obj=member)

        return render_template('message/messagesend.html', form=form)


@app.route('/mymessagereadall')
@login_required
def mymessagereadall():
    messagelist = Message.query.filter(Message.touid == session['uid']).all()
    for message in messagelist:
        if not message.readtime:
            message.update_readtime()
            db.session.add(message)
    db.session.commit()
    flash({'type': 'success', 'content': '所有消息已标为已读。'})
    return redirect(url_for('mymessage'))
