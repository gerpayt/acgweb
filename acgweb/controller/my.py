# coding: utf-8
from flask import render_template, json, abort, flash, make_response
from acgweb import app, db
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from acgweb.model.message import Message
from acgweb.model.member import Member
from acgweb.form.member import MemberForm
import acgweb.const as CONST
from decorated_function import *
import notify

@app.route('/myactivity-p<int:pagenum>')
@app.route('/myactivity')
@login_required
def myactivity(pagenum=1):
    """Page: all activitylist"""
    # TODO status!=0
    duty_count = Duty.query.filter(Duty.uid == session[u'uid']).count()
    duty_list = Duty.query.filter(Duty.uid == session[u'uid']).order_by('activity_1_start_time DESC').limit(CONST.activity_per_page).offset(CONST.activity_per_page * (pagenum - 1))
    if viewtype() == 1:
        return render_template('my/myactivity_mobile.html',
            duty_list=duty_list,
            page_count=(duty_count - 1) / CONST.activity_per_page + 1, page_current=pagenum)
    else:
        return render_template('my/myactivity.html',
            duty_list=duty_list,
            page_count=(duty_count - 1) / CONST.activity_per_page + 1, page_current=pagenum)


@app.route('/api/myactivitylist')
@return_json
def myactivityapi(me):
    activity_list = Activity.query.join(Duty).filter(Duty.uid == me.uid).order_by(Activity.start_time).all()
    res = []
    for activity in activity_list:
        d = {}
        d['id'] = activity.id
        d['title'] = activity.title
        d['venue'] = activity.venue
        d['remark'] = activity.remark
        d['work_start_time'] = activity.work_start_time
        d['start_time'] = activity.start_time
        d['end_time'] = activity.end_time
        d['type'] = activity.type
        d['status'] = activity.status
        d['duties'] = [{'uid': x.member.uid, 'name': x.member.name, 'status': x.status} for x in activity.duties]
        res.append(d)
    return res


@app.route('/myinfo', methods=['GET', 'POST'])
@login_required
def myinfo():
    if request.method == 'POST':
        member = Member.query.get_or_404(session['uid'])
        form = MemberForm(request.form)
        if form.validate_on_submit():
            if Member.query.filter(Member.email == form.email.data, Member.uid != session[u'uid']).count():
                form.email.errors.append('电子邮箱已存在')
            if Member.query.filter(Member.mobile_num == form.mobile_num.data, Member.uid != session[u'uid']).count():
                form.mobile_num.errors.append('手机号码已存在')

        if not form.errors:
            if member and member.uid != session[u'uid']:
                abort(403)
            if not member: member = Member()
            member.uid = session[u'uid']
            member.name = form.name.data.replace(' ', '')
            member.sex = form.sex.data
            member.school = form.school.data.replace(' ', '')
            member.mobile_num = form.mobile_num.data.replace(' ', '')
            member.mobile_type = form.mobile_type.data
            member.mobile_short = form.mobile_short.data.replace(' ', '')
            member.qqnum = form.qqnum.data.replace(' ', '')
            member.email = form.email.data.replace(' ', '')
            member.address = form.address.data.replace(' ', '')
            member.mobile_num2 = form.mobile_num2.data.replace(' ', '')
            member.credit_card = form.credit_card.data.replace(' ', '')
            member.introduce = form.introduce.data
            session['name'] = member.name
            db.session.add(member)
            db.session.commit()

            flash({'type': 'success', 'content': '保存成功！'})
            return redirect('/myinfo')
        #print form.errors
        if viewtype() == 1:
            return render_template('my/myinfo_mobile.html', form=form, member=member)
        else:
            return render_template('my/myinfo.html', form=form, member=member)
    else:
        member = Member.query.get_or_404(session['uid'])
        if member.uid != session[u'uid']:
            abort(403)
        form = MemberForm(obj=member)

        if viewtype() == 1:
            return render_template('my/myinfo_mobile.html', form=form, member=member)
        else:
            return render_template('my/myinfo.html', form=form, member=member)


@app.route('/api/myinfo', methods=['GET', 'POST'])
@return_json
def myinfoapi(me):
    if request.method == 'POST':
        #TODO
        member = Member.query.get(uid)
        form = MemberForm(request.form)
        if form.validate_on_submit():
            if Member.query.filter(Member.email == form.email.data, Member.uid != uid).count():
                form.email.errors.append('电子邮箱已存在')
            if Member.query.filter(Member.mobile_num == form.mobile_num.data, Member.uid != uid).count():
                form.mobile_num.errors.append('手机号码已存在')

        if not form.errors:
            if member and member.uid != uid:
                abort(403)
            if not member: member = Member()
            member.uid = uid
            member.name = form.name.data
            member.sex = form.sex.data
            member.school = form.school.data
            member.mobile_num = form.mobile_num.data
            member.mobile_type = form.mobile_type.data
            member.mobile_short = form.mobile_short.data
            member.qqnum = form.qqnum.data
            member.email = form.email.data
            member.address = form.address.data
            member.credit_card = form.credit_card.data
            member.introduce = form.introduce.data
            session['name'] = member.name
            db.session.add(member)
            db.session.commit()

            flash({'type': 'success', 'content': '保存成功！'})
            return redirect('/myinfo')

    else:
        member = Member.query.get(me.uid)

        res = {}
        res['uid'] = member.uid
        res['name'] = member.name
        res['type'] = member.type
        res['sex'] = member.sex
        res['school'] = member.school
        res['mobile'] = member.mobile_num
        res['mobile_type'] = member.mobile_type
        res['mobile_short'] = member.mobile_short
        res['email'] = member.email
        res['qqnum'] = member.qqnum
        res['address'] = member.address
        res['credit_card'] = member.credit_card
        res['introduce'] = member.introduce
        res['photo'] = member.photo
        res['register_time'] = member.register_time
        res['lastlogin_time'] = member.lastlogin_time

        return res


@app.route('/mysetting-reset')
@login_required
def mysettingreset():
    member = Member.query.get_or_404(session['uid'])
    setting = notify.default_setting.copy()
    member.setting = json.dumps(setting)
    #print setting
    db.session.add(member)
    db.session.commit()
    flash({'type': 'success', 'content': '重置成功。'})

    return redirect(url_for('mysetting'))


@app.route('/mysetting', methods=['GET', 'POST'])
@login_required
def mysetting():
    member = Member.query.get_or_404(session['uid'])
    if request.method == 'POST':
        setting = notify.empty_setting.copy()
        for item in request.form:
            #print item, request.form[item]
            (x, event, method) = item.split('-')
            setting[event+'-'+method] = int(request.form[item])
        #print setting
        member.setting = json.dumps(setting)
        db.session.add(member)
        db.session.commit()
        flash({'type': 'success', 'content': '修改成功。'})

    else:
        setting = notify.default_setting.copy()
        if member.setting != '':
            setting.update(json.loads(member.setting))

    setting_list = notify.notify_setting_list

    return render_template('my/mysetting.html', setting=setting, setting_list=setting_list)


@app.before_request
def check_new_message():
    if session.has_key(u'uid'):
        message_count = Message.query.filter(Message.touid == session[u'uid'], Message.readtime == 0).count()
    else:
        message_count = 0
    session['new_message'] = message_count
    #print session
