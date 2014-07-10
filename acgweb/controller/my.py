# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, abort, flash
from acgweb import app, db
from acgweb.model.duty import Duty
from acgweb.model.message import Message
from acgweb.model.member import Member
from acgweb.form.member import MemberForm
import acgweb.const as CONST
from acgweb import config
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
    if viewtype()==1:
        return render_template('my/myactivity_mobile.html',
            duty_list=duty_list,
            page_count=(duty_count-1)/CONST.activity_per_page+1,page_current=pagenum)
    else:
        return render_template('my/myactivity.html',
            duty_list=duty_list,
            page_count=(duty_count-1)/CONST.activity_per_page+1,page_current=pagenum)


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
        #print form.errors
        if viewtype()==1:
            return render_template('my/myinfo_mobile.html', form=form, member=member)
        else:
            return render_template('my/myinfo.html', form=form, member=member)
    else:
        member = Member.query.get_or_404(session['uid'])
        if member.uid != session[u'uid']:
            abort(403)
        form = MemberForm(obj=member)

        if viewtype()==1:
            return render_template('my/myinfo_mobile.html', form=form, member=member)
        else:
            return render_template('my/myinfo.html', form=form, member=member)


@app.before_request
def check_new_message():
    if session.has_key(u'uid'):
        message_count = Message.query.filter(Message.touid==session[u'uid'], Message.readtime==0).count()
    else:
        message_count = 0
    session['new_message'] = message_count
    #print session

