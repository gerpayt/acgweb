# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, abort, flash
from acgweb import app, db
from acgweb.model.duty import Duty
from acgweb.model.message import Message
from acgweb.model.schedule import Schedule
from acgweb.model.member import Member
from acgweb.form.schedule import ScheduleForm
from acgweb.form.member import MemberForm
import acgweb.const as CONST
import template_filter
from decorated_function import *
import time

@app.route('/myactivity-p<int:pagenum>')
@app.route('/myactivity')
@login_required
def myactivity(pagenum=1):
    """Page: all activitylist"""
    # TODO status!=0
    duty_count = Duty.query.filter(Duty.uid==session[u'uid']).count()
    duty_list = Duty.query.filter(Duty.uid==session[u'uid']).order_by('activity_1_start_time ASC').limit(CONST.activity_per_page).offset(CONST.activity_per_page*(pagenum-1))
    return render_template('my/myactivity.html',
        duty_list=duty_list,
        page_count=(duty_count-1)/CONST.activity_per_page+1,page_current=pagenum)


@app.route('/myschedule')
@login_required
def myschedule():
    """Page: all activitylist"""
    schedule_list = Schedule.query.filter(Schedule.uid==session[u'uid']).all()
    return render_template('my/myschedule.html',
        schedule_list=schedule_list,)


@app.route('/myschedule_form', methods=['GET', 'POST'])
@app.route('/myschedule_form-<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def myschedule_form(schedule_id=0):
    """Page: all activitylist"""
    if request.method == 'POST':
        form = ScheduleForm(request.form)
        if form.validate_on_submit():
            if not form.errors:
                pass#form.username.errors.append('帐号已存在')
        if not form.errors:
            schedule = Schedule.query.get(form.id.data)
            if schedule and schedule.uid != session[u'uid']:
                abort(403)
            if not schedule: schedule = Schedule()
            schedule.uid=session[u'uid']
            schedule.week=form.week.data
            schedule.weekday=form.weekday.data
            schedule.section=form.section.data
            schedule.classname=form.classname.data
            schedule.classtype=form.classtype.data
            schedule.update_semester()
            db.session.add(schedule)
            db.session.commit()

            flash({'type':'success', 'content':'保存成功！'})
            return redirect('/myschedule')
        return render_template('my/myschedule-form.html', form=form)
    else:
        if schedule_id:
            schedule = Schedule.query.get_or_404(schedule_id)
            if schedule.uid != session[u'uid']:
                abort(403)
            form = ScheduleForm(obj=schedule)
        else:
            form = ScheduleForm()
        return render_template('my/myschedule-form.html', form=form)


@app.route('/mymessage-p<int:pagenum>')
@app.route('/mymessage')
@login_required
def mymessage(pagenum=1):
    """Page: all activitylist"""
    message_count = Message.query.filter(Message.touid==session[u'uid']).count()
    message_list = Message.query.filter(Message.touid==session[u'uid']).order_by('sendtime DESC').\
        limit(CONST.message_per_page).offset(CONST.message_per_page*(pagenum-1))
    return render_template('my/mymessage.html',
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
    return render_template('my/mymessage.html',
        message_list=message_list)
'''

@app.route('/mymessagedetail-<int:message_id>')
@login_required
def mymessagedetail(message_id=0):
    message = Message.query.get_or_404(message_id)
    if not message.readtime:
        message.update_readtime()
        db.session.add(message)
        db.session.commit()
    return render_template('my/mymessagedetail.html',
        message=message)


@app.route('/myinfo', methods=['GET', 'POST'])
@login_required
def myinfo():

    if request.method == 'POST':
        member = Member.query.get_or_404(session['uid'])
        form = MemberForm(request.form)
        if form.validate_on_submit():
            if Member.query.filter(Member.email==form.email.data, Member.uid != session[u'uid']).count():
                form.email.errors.append('电子邮箱已存在')
            if Member.query.filter(Member.mobile_num==form.mobile_num.data, Member.uid != session[u'uid']).count():
                form.mobile_num.errors.append('手机号码已存在')

        if not form.errors:
            if member and member.uid != session[u'uid']:
                abort(403)
            if not member: member = Member()
            member.uid=session[u'uid']
            member.name=form.name.data
            member.sex=form.sex.data
            member.school=form.school.data
            member.mobile_num=form.mobile_num.data
            member.mobile_type=form.mobile_type.data
            member.mobile_short=form.mobile_short.data
            member.qqnum=form.qqnum.data
            member.email=form.email.data
            member.address=form.address.data
            member.credit_card=form.credit_card.data
            member.introduce=form.introduce.data
            session['name']=member.name
            db.session.add(member)
            db.session.commit()

            flash({'type':'success', 'content':'保存成功！'})
            return redirect('/myinfo')
        print form.errors
        return render_template('my/myinfo.html', form=form, member=member)
    else:
        member = Member.query.get_or_404(session['uid'])
        if member.uid != session[u'uid']:
            abort(403)
        form = MemberForm(obj=member)

        return render_template('my/myinfo.html', form=form, member=member)


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

        return render_template('my/mymessagesend.html', form=form)

@app.before_request
def check_new_message():
    if session.has_key(u'uid'):
        message_count = Message.query.filter(Message.touid==session[u'uid'], Message.readtime==0).count()
    else:
        message_count = 0
    session['new_message'] = message_count
    #print session

