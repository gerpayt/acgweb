# coding: utf-8

import time

from flask import render_template, json, flash, jsonify, abort, make_response
from acgweb import db
from sqlalchemy import or_
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from acgweb.model.schedule import Schedule
from acgweb.model.member import Member
from acgweb.form.activity import ActivityForm
from acgweb import config
from template_filter import *
from decorated_function import *
from acgweb.controller import mail
from acgweb.controller import sms
import notify

@app.route('/activitylist-p<int:pagenum>')
@app.route('/activitylist')
@login_required
def activitylist(pagenum=1):
    ts = time.localtime()
    todaytime = int(time.time()) - ts.tm_hour * 3600 - ts.tm_min * 60 - ts.tm_sec
    activity_count = Activity.query.filter(Activity.start_time > todaytime, Activity.status != CONST.ACTIVITY_UNKNOWN).count()
    activity_list = Activity.query.filter(Activity.start_time > todaytime, Activity.status != CONST.ACTIVITY_UNKNOWN)\
        .order_by(Activity.start_time).limit(CONST.activity_per_page).offset(CONST.activity_per_page * (pagenum - 1))
    if viewtype() == 1:
        return render_template('activity/activitylist_mobile.html', activity_list=activity_list,
                               page_count=(activity_count - 1) / CONST.activity_per_page + 1, page_current=pagenum)
    else:
        return render_template('activity/activitylist.html', activity_list=activity_list,
                               page_count=(activity_count - 1) / CONST.activity_per_page + 1, page_current=pagenum)


@app.route('/api/activitylist')
#@login_required
def activitylistapi():
    ts = time.localtime()
    todaytime = int(time.time()) - ts.tm_hour * 3600 - ts.tm_min * 60 - ts.tm_sec
    activity_list = Activity.query.filter(Activity.start_time > todaytime, Activity.status != CONST.ACTIVITY_UNKNOWN)\
        .order_by(Activity.start_time).all()
    res = []
    for activity in activity_list:
        d = {}
        d['id'] = activity.id
        d['title'] = activity.title
        d['venue'] = activity.venue
        d['status'] = activity.status
        d['start_time'] = activity.start_time
        d['duties'] = [{'uid': x.member.uid, 'name': x.member.name, 'status': x.status} for x in activity.duties]
        res.append(d)
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/activitymanage-p<int:pagenum>')
@app.route('/activitymanage')
@login_required
def activitymanage(pagenum=1):
    if not session.get('is_arra_monitor'):
        abort(403)
    ts = time.localtime()
    todaytime = int(time.time()) - ts.tm_hour * 3600 - ts.tm_min * 60 - ts.tm_sec
    #config.SEMESTER_BASE
    activity_count = Activity.query.filter(Activity.start_time >= todaytime - 3 * 86400).count()
    activity_list = Activity.query.filter(Activity.start_time >= todaytime - 3 * 86400).order_by(Activity.start_time)\
        .limit(CONST.activity_per_page).offset(CONST.activity_per_page * (pagenum - 1))
    return render_template('activity/activitymanage.html', activity_list=activity_list,
                           page_count=(activity_count - 1) / CONST.activity_per_page + 1, page_current=pagenum)


@app.route('/activity-<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activitydetail(activity_id):
    if request.method == 'GET':
        activity = Activity.query.get_or_404(activity_id)
        is_busy = Duty.query.filter(Duty.uid == session['uid'], Duty.aid == activity_id).count()
        duty = Duty.query.filter(Duty.uid == session['uid'], Duty.aid == activity_id).first()
        if duty:
            is_success = (duty.status == CONST.DUTY_ACTIVITY_ONGOING)
        else:
            is_success = False
        now = int(time.time())
        on_schedule = False
        st = activity.getstrustarttime()
        schedulelist = Schedule.query.filter(Schedule.uid == session['uid'], Schedule.semester == config.SEMESTER).all()
        for s in schedulelist:
            s.strtolist()
            #print st['week'], s.weeklist, st['weekday'], s.weekdaylist
            if st['week'] in s.weeklist and st['weekday'] in s.weekdaylist:
                if st['start_section'] in s.sectionlist or st['start_section'] + 3 in s.sectionlist:
                    on_schedule = s.classname
                    break
        #print busymember
        if viewtype() == 1:
            return render_template('activity/activitydetail_mobile.html',
                                   activity=activity, is_busy=is_busy, is_success=is_success, on_schedule=on_schedule, now=now)
        else:
            return render_template('activity/activitydetail.html',
                                   activity=activity, is_busy=is_busy, is_success=is_success, on_schedule=on_schedule, now=now)
    else:
        activity = Activity.query.get(activity_id)
        if activity.status == CONST.ACTIVITY_ONGOING or activity.status == CONST.ACTIVITY_ENDED:
            duty = Duty.query.filter(Duty.aid == activity_id, Duty.uid == session['uid']).first()

            type = request.form['type']
            content = request.form['content']
            duty.appendlog(type, content)
            db.session.add(activity)
            db.session.commit()
            # 根据不同的类型来通知不同的人 #TODO
            return jsonify(result='ok', msg='成功')
        else:
            return jsonify(result='err', msg='非法操作，请重试。')


@app.route('/api/activitydetail-<int:activity_id>', methods=['GET', 'POST'])
#@login_required
def activitydetailapi(activity_id):
    """Page: activity detail"""
    if request.method == 'GET':
        activity = Activity.query.get(activity_id)
        uid = request.args.get('uid')
        is_busy = Duty.query.filter(Duty.uid == uid, Duty.aid == activity_id).count()
        duty = Duty.query.filter(Duty.uid == uid, Duty.aid == activity_id).first()
        if duty:
            is_success = duty.status == CONST.DUTY_ACTIVITY_ONGOING
        else:
            is_success = False
        now = int(time.time())
        d = {}
        d['is_busy'] = is_busy
        d['is_success'] = is_success
        d['id'] = activity.id
        d['title'] = activity.title
        d['venue'] = activity.venue
        d['remark'] = activity.remark
        d['status'] = activity.status
        d['start_time'] = activity.start_time
        d['end_time'] = activity.end_time
        d['duties'] = [{'uid': x.member.uid, 'name': x.member.name, 'mobile': x.member.mobile_num, 'status': x.status} for x in activity.duties]
        res = d #, 'is_busy': is_busy, 'is_success': is_success, 'now': now}
        resp = make_response(json.dumps(res))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    else:
        activity = Activity.query.get(activity_id)
        if activity.status == CONST.ACTIVITY_ONGOING or activity.status == CONST.ACTIVITY_ENDED:
            duty = Duty.query.filter(Duty.aid == activity_id, Duty.uid == session['uid']).first()

            type = request.form['type']
            content = request.form['content']
            duty.appendlog(type, content)
            db.session.add(activity)
            db.session.commit()
            # 根据不同的类型来通知不同的人 #TODO
            return jsonify(result='ok', msg='成功')
        else:
            return jsonify(result='err', msg='非法操作，请重试。')


@app.route('/activityoperation-<operation>-<int:duty_id>', methods=['GET', 'POST'])
@login_required
def activityoperation(operation, duty_id):
    duty = Duty.query.get_or_404(duty_id)
    if duty.activity.status == CONST.ACTIVITY_SCHEDULING:
        if ((session['uid'] == duty.member.uid and operation in CONST.duty_status_operation_selfuser_mapper[duty.status]) or
            (session['uid'] != duty.member.uid and operation in CONST.duty_status_operation_otheruser_mapper[duty.status]) or
            (session.get('is_arra_monitor') and operation in CONST.duty_status_operation_monitor_mapper[duty.status])):
            # 一个活动一个成员只能有一条值班记录
            if operation in ['activity_appoint', 'approve_apply']:
                target_uid = duty.uid
            elif operation in ['apply_duty', 'confirm_apply', 'accept_duty', 'cover_duty']:
                target_uid = session['uid']
            else:
                target_uid = ''

            if not Duty.query.filter(Duty.id != duty_id, Duty.uid == target_uid, Duty.aid == duty.aid).count():
                #print Article.query.filter(Article.title==article_title).statement
                if request.method == 'POST':
                    reason = request.form['content']
                else:
                    reason = ''
                if CONST.dutyoperationname[operation].has_key('require_input') and not reason:
                    flash({'type': 'error', 'content': '请填写申请理由。'})
                    return redirect(url_for('activitydetail', activity_id=duty.aid))

                duty.status = CONST.duty_status_operation_next[operation]
                duty.appendprocesse(operation, reason)
                db.session.add(duty)
                db.session.commit()

                if operation == 'cover_duty':
                    if Duty.query.filter(Duty.uid == session['uid'], Duty.aid == duty.aid).count():
                        flash({'type': 'danger', 'content': '你在本时间段已经有此活动，请勿重复选班。'})
                        return redirect(url_for('activitydetail', activity_id=duty.aid))
                    else:
                        new_duty = Duty(aid=duty.aid, uid=session['uid'], status=CONST.DUTY_BEFORE_START, log='')
                        new_duty.appendprocesse('cover_duty', '')
                        db.session.add(new_duty)
                        db.session.commit()

                        worktimestr = timeformat_filter(duty.activity.work_start_time, "%Y-%m-%d %H:%M")
                        timestr = timeformat_filter(duty.activity.start_time, "%Y-%m-%d %H:%M")
                        venue = venuename_filter(duty.activity.venue)
                        title = duty.activity.title
                        remark = duty.activity.remark
                        url = config.BASE_URL + url_for('activitydetail', activity_id=duty.activity.id)
                        member_url = config.BASE_URL + url_for('memberdetail', member_uid=session['uid'])
                        member_name = session['name']

                        subject = mail.cover_duty_tmpl['subject']
                        content = mail.cover_duty_tmpl['content'] % (member_url, member_name, worktimestr, timestr, venue, title, remark, url, url)
                        sms_content = sms.sms_cover_duty_tmpl % (member_name, worktimestr, venue, title)
                        if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_COVER_DUTY):
                            msg_id = mail.send_message(duty.uid, session['uid'], subject, content, 2)
                        else:
                            msg_id = 0
                        if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_COVER_DUTY):
                            mail.send_mail(subject, content, duty.member.name, duty.member.email,
                                           msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
                        if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_COVER_DUTY):
                            pass  # TODO app notify
                        if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_COVER_DUTY):
                            sms.send_sms(duty.member.mobile_num, sms_content)

                elif operation == 'approve_apply' or operation == 'decline_apply':
                    worktimestr = timeformat_filter(duty.activity.work_start_time, "%Y-%m-%d %H:%M")
                    timestr = timeformat_filter(duty.activity.start_time, "%Y-%m-%d %H:%M")
                    venue = venuename_filter(duty.activity.venue)
                    title = duty.activity.title
                    remark = duty.activity.remark
                    url = config.BASE_URL + url_for('activitydetail', activity_id=duty.activity.id)
                    if operation == 'approve_apply':
                        subject = mail.approve_apply_tmpl['subject']
                        content = mail.approve_apply_tmpl['content'] % (worktimestr, timestr, venue, title, remark, url, url)
                        sms_content = sms.sms_approve_apply_tmpl % (worktimestr, venue, title)
                        if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_APPROVE_APPLY):
                            msg_id = mail.send_message(duty.uid, session['uid'], subject, content, 2)
                        else:
                            msg_id = 0
                        if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_APPROVE_APPLY):
                            mail.send_mail(subject, content, duty.member.name, duty.member.email, msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
                        if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_APPROVE_APPLY):
                            pass  # TODO app notify
                        if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_APPROVE_APPLY):
                            sms.send_sms(duty.member.mobile_num, sms_content)
                    else:
                        subject = mail.decline_apply_tmpl['subject']
                        content = mail.decline_apply_tmpl['content'] % (worktimestr, timestr, venue, title, remark, url, url)
                        sms_content = sms.sms_decline_apply_tmpl % (worktimestr, venue, title)
                        if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_APPROVE_APPLY):
                            msg_id = mail.send_message(duty.uid, session['uid'], subject, content, 2)
                        else:
                            msg_id = 0
                        if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_APPROVE_APPLY):
                            mail.send_mail(subject, content, duty.member.name, duty.member.email, msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
                        if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_APPROVE_APPLY):
                            pass  # TODO app notify
                        if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_APPROVE_APPLY):
                            sms.send_sms(duty.member.mobile_num, sms_content)
                elif operation == 'decline_duty':
                    uname = session['name']
                    worktimestr = timeformat_filter(duty.activity.work_start_time, "%Y-%m-%d %H:%M")
                    timestr = timeformat_filter(duty.activity.start_time, "%Y-%m-%d %H:%M")
                    venue = venuename_filter(duty.activity.venue)
                    title = duty.activity.title
                    remark = duty.activity.remark
                    url = config.BASE_URL + url_for('activitydetail', activity_id=duty.activity.id)
                    subject = mail.decline_duty_tmpl['subject']
                    content = mail.decline_duty_tmpl['content'] % (uname, reason, worktimestr, timestr, venue, title, remark, url, url)
                    sms_content = sms.sms_decline_duty_tmpl % (uname, worktimestr, venue, title)
                    for uid in config.ARRA_MONITOR:
                        member = Member.query.get(uid)
                        if notify.is_notify(uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_DECLINE_DUTY):
                            msg_id = mail.send_message(uid, session['uid'], subject, content, 2)
                        else:
                            msg_id = 0
                        if notify.is_notify(uid, notify.NOTIFY_EMAIL, notify.NOTIFY_DECLINE_DUTY):
                            mail.send_mail(subject, content, member.name, member.email, msgid=msg_id, touid=uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
                        if notify.is_notify(uid, notify.NOTIFY_APP, notify.NOTIFY_DECLINE_DUTY):
                            pass  # TODO app notify
                        if notify.is_notify(uid, notify.NOTIFY_SMS, notify.NOTIFY_DECLINE_DUTY):
                            sms.send_sms(duty.member.mobile_num, sms_content)

                elif operation == 'cancel_task':
                    pass#timestr = timeformat_filter(duty.activity.start_time,"%Y-%m-%d %H:%M")
                    #venue = venuename_filter(duty.activity.venue)
                    #title = duty.activity.title
                    #remark = duty.activity.remark
                    #url = config.BASE_URL + url_for('activitydetail',activity_id=duty.activity.id)
                    #subject = mail.approve_apply_tmpl['subject']
                    #content = mail.approve_apply_tmpl['content'] % ( timestr, venue, title, remark, url , url )
                    #msg_id = mail.send_message(duty.uid,session['uid'],subject,content,2)
                    #mail.send_mail(subject, content, duty.member.name, duty.member.email, msg_id)


                flash({'type': 'success', 'content': '操作成功！'})
            else:
                flash({'type': 'danger', 'content': '一个活动只能选一个班。'})
        else:
            flash({'type': 'danger', 'content': '没有权限。'})
    else:
        flash({'type': 'danger', 'content': '过期操作。'})
    return redirect(url_for('activitydetail', activity_id=duty.aid))


@app.route('/activityapply-<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activityapply(activity_id):
    """Page: activity detail"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == CONST.ACTIVITY_SCHEDULING and (not Duty.query.filter(Duty.uid == session['uid'], Duty.aid == activity_id).count()):
        content = request.form['content']
        if not content:
            flash({'type': 'error', 'content': '请填写申请理由。'})
        else:
            newduty = Duty(aid=activity_id, uid=session['uid'], status=CONST.DUTY_APPLY_ING, process='', log='')
            newduty.appendprocesse('apply_duty', content)
            db.session.add(newduty)
            db.session.commit()
            flash({'type': 'success', 'content': '值班申请提交成功，等待排版班长审核。'})
    else:
        flash({'type': 'danger', 'content': '非法操作，请重试。'})
    return redirect(url_for('activitydetail', activity_id=activity_id))


@app.route('/activityedit', methods=['GET', 'POST'])
@app.route('/activityedit-<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activityedit(activity_id=0):
    if request.method == 'POST':
        form = ActivityForm(request.form)
        if form.validate_on_submit():
            if not form.errors:
                pass#form.username.errors.append('帐号已存在')
        #print form.errors
        if not form.errors:
            activity = Activity.query.get(form.id.data)
            if not session.get('is_arra_monitor'):
                abort(403)
            if not activity:
                activity = Activity()

            info_modify = str(activity.title) != str(form.title.data) or str(activity.venue) != str(form.venue.data) or str(activity.work_start_time) != str(form.work_start_time.data)
            if info_modify:
                if int(activity.work_start_time) == int(form.work_start_time.data):
                    worktimestr_modify = u'%s 不变' % timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M")
                else:
                    worktimestr_modify = u'<strong>%s 变为 %s</strong>' % (timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M"), timeformat_filter(form.work_start_time.data, "%Y-%m-%d %H:%M"))
                if int(activity.start_time) == int(form.start_time.data):
                    timestr_modify = u'%s 不变' % timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M")
                else:
                    timestr_modify = u'<strong>%s 变为 %s</strong>' % (timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M"), timeformat_filter(form.start_time.data, "%Y-%m-%d %H:%M"))
                if activity.venue == form.venue.data:
                    venue_modify = u'%s 不变' % venuename_filter(activity.venue)
                else:
                    venue_modify = u'<strong>%s 变为 %s</strong>' % (venuename_filter(activity.venue), venuename_filter(form.venue.data))
                if activity.title == form.title.data:
                    title_modify = u'%s 不变' % activity.title
                else:
                    title_modify = u'<strong>%s 变为 %s</strong>' % (activity.title, form.title.data)
                remark = activity.remark
                url = config.BASE_URL + url_for('activitydetail', activity_id=activity.id)
                subject = mail.activity_modify_tmpl['subject']
                content = mail.activity_modify_tmpl['content'] % (worktimestr_modify, timestr_modify, venue_modify, title_modify, remark, url, url)
                sms_content = sms.sms_activity_modify_tmpl % (worktimestr_modify, venue_modify, title_modify)

            activity.title = form.title.data
            activity.remark = form.remark.data
            activity.venue = form.venue.data
            activity.work_start_time = form.work_start_time.data
            activity.start_time = form.start_time.data
            activity.end_time = form.end_time.data
            activity.type = form.type.data
            activity.status = form.status.data
            activity.hostname = form.hostname.data
            db.session.add(activity)
            db.session.commit()

            if info_modify:
                dutylist = Duty.query.filter(Duty.aid == activity_id).all()

                for duty in dutylist:
                    if duty.status in [CONST.DUTY_APPLY_ING, CONST.DUTY_APPLY_CONFIRM, CONST.DUTY_ARRANGE_CONFIRM, CONST.DUTY_BEFORE_START, CONST.DUTY_REPLACE_ING]:
                        if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_ACTIVITY_MODIFY):
                            msg_id = mail.send_message(duty.uid, session['uid'], subject, content, 2)
                        else:
                            msg_id = 0
                        if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_ACTIVITY_MODIFY):
                            mail.send_mail(subject, content, duty.member.name, duty.member.email, msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
                        if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_ACTIVITY_MODIFY):
                            pass  # TODO app notify
                        if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_ACTIVITY_MODIFY):
                            sms.send_sms(duty.member.mobile_num, sms_content)

            flash({'type': 'success', 'content': '保存成功！'})
            return redirect('/activitymanage')
        return render_template('activity/activityedit.html', form=form)

    else:
        activity = Activity.query.get(activity_id)
        if not session.get('is_arra_monitor'):
            abort(403)
        form = ActivityForm(obj=activity)
        if Duty.query.filter(Duty.aid == activity_id).count():
            flash({'type': 'warning', 'content': '已有音控员负责此活动，请谨慎操作！'})
        return render_template('activity/activityedit.html', form=form)


@app.route('/activityarrange-<int:activity_id>')
@login_required
def activityarrange(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    st = activity.getstrustarttime()
    available_member = {}
    schedule_content = {}
    if activity.status == CONST.ACTIVITY_SCHEDULING and session.get('is_arra_monitor'):
        schedulelist = Schedule.query.filter(Schedule.semester == config.SEMESTER).all()
        memberlist = Member.query.filter(or_(Member.type == 1, Member.type == 3)).order_by('convert(name using gb2312) ASC').all()
        busymember = {}
        scheduletable = {}
        for s in schedulelist:
            if busymember.has_key(s.uid):
                continue
            s.strtolist()
            #print st['week'], s.weeklist, st['weekday'], s.weekdaylist
            if st['week'] in s.weeklist and st['weekday'] in s.weekdaylist:
                if not scheduletable.has_key(s.uid):
                    scheduletable[s.uid] = {}
                #scheduletable[s.uid][]
                if st['start_section'] in s.sectionlist or st['start_section'] + 3 in s.sectionlist:
                    busymember[s.uid] = s.classtype
        #print busymember
        hour = time.localtime(activity.start_time).tm_hour
        #print activity.start_time,hour
        starttime = activity.start_time - 2 * 3600
        endtime = activity.start_time + 3 * 3600
        activitylist = Activity.query.filter(Activity.start_time >= starttime, Activity.start_time <= endtime).all()
        for a in activitylist:
            for d in a.duties:
                busymember[d.uid] = 9
        for member in memberlist:
            m = {'uid': member.uid, 'name': member.name, 'mobile_num': member.mobile_num, 'qqnum': member.qqnum, 'email': member.email,
                 'available': busymember.get(member.uid, 0), 'venue': 0, 'start_time': 0, 'weekcount': 0, 'monthcount': 0}
            available_member[member.uid] = m
            try:
                fp = open(config.BASE_DIR + 'cache/st_%s.log' % member.uid, 'r')
                activity_timestr = time.strftime("%Y-%m-%d", time.localtime(activity.start_time))
                for line in fp:
                    timestr = line[:10]
                    if timestr == activity_timestr:
                        line = line.rstrip('\n')
                        schedule_content[member.uid] = line[11:].split('\t')
                        break
                fp.close()
            except:
                schedule_content[member.uid] = []

        # get last duty time and venue
        sql = "select a.uid, b.venue, max(b.work_start_time) as start_time from duty as a left join activity as b on a.aid = b.id where a.status=" + str(CONST.DUTY_ACTIVITY_ENDED) +" group by a.uid"
        res = db.session.execute(sql)
        for r in res:
            (uid, venue, work_start_time) = r
            if uid in available_member.keys():
                available_member[uid]['venue'] = venue
                available_member[uid]['work_start_time'] = work_start_time

        # get last week and last month count
        sql = "select a.uid, count(1) as count from duty as a left join activity as b on a.aid = b.id where a.status=" + str(CONST.DUTY_ACTIVITY_ENDED) +" and b.start_time<= %d and b.start_time>= %d group by a.uid"
        now = int(time.time())
        last_week = now - 7 * 86400
        last_month = now - 30 * 86400
        res = db.session.execute(sql % (now, last_week))
        #print sql%(now, last_week)
        for r in res:
            (uid, weekcount) = r
            if uid in available_member.keys():
                available_member[uid]['weekcount'] = weekcount
        res = db.session.execute(sql % (now, last_month))
        for r in res:
            (uid, monthcount) = r
            if uid in available_member.keys():
                available_member[uid]['monthcount'] = monthcount

    else:
        flash({'type': 'danger', 'content': '非法操作，请重试。'})
    #print available_member.values()
    # TODO sort name list
    return render_template('activity/activityarrange.html', activity=activity, schedule_content=schedule_content, available_member=available_member.values())


@app.route('/activityappoint-<int:activity_id>-<member_uid>')
@login_required
def activityappoint(activity_id, member_uid):
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == CONST.ACTIVITY_SCHEDULING and session.get('is_arra_monitor'):
        member = Member.query.get(member_uid)
        if not Duty.query.filter(Duty.aid == activity_id, Duty.uid == member_uid).count():
            duty = Duty()
            duty.aid = activity_id
            duty.uid = member_uid
            duty.status = CONST.DUTY_ARRANGE_CONFIRM
            duty.log = ''
            duty.appendprocesse('activity_appoint', '排班班长安排值班')
            db.session.add(duty)
            db.session.commit()
            # need or not
            timestr = timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M")
            worktimestr = timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M")
            venue = venuename_filter(activity.venue)
            title = activity.title
            remark = activity.remark
            url = config.BASE_URL + url_for('activitydetail', activity_id=activity.id)
            subject = mail.activity_appoint_tmpl['subject']
            content = mail.activity_appoint_tmpl['content'] % (worktimestr, timestr, venue, title, remark, url, url)
            sms_content = sms.sms_activity_appoint_tmpl % (worktimestr, venue, title)
            if notify.is_notify(member_uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_ACTIVITY_APPOINT):
                msg_id = mail.send_message(member_uid, session['uid'], subject, content, 2)
            else:
                msg_id = 0
            if notify.is_notify(member_uid, notify.NOTIFY_EMAIL, notify.NOTIFY_ACTIVITY_APPOINT):
                mail.send_mail(subject, content, member.name, member.email, msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
            if notify.is_notify(member_uid, notify.NOTIFY_APP, notify.NOTIFY_ACTIVITY_APPOINT):
                pass  # TODO app notify
            if notify.is_notify(member_uid, notify.NOTIFY_SMS, notify.NOTIFY_ACTIVITY_APPOINT):
                sms.send_sms(duty.member.mobile_num, sms_content)
        else:
            flash({'type': 'danger', 'content': '此人已经安排过值班任务。'})
    else:
        flash({'type': 'danger', 'content': '非法操作，请重试。'})
    return redirect(url_for('activitydetail', activity_id=activity_id))


@app.route('/activityready-<int:activity_id>')
@login_required
def activityready(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == CONST.ACTIVITY_UNKNOWN and session.get('is_arra_monitor'):
        #print Article.query.filter(Article.title==article_title).statement
        flash({'type': 'success', 'content': '活动已经就绪。'})
        activity = Activity.query.get_or_404(activity_id)
        activity.status = CONST.ACTIVITY_SCHEDULING
        db.session.add(activity)
        db.session.commit()
    else:
        flash({'type': 'danger', 'content': '非法操作，请重试。'})
    return redirect(url_for('activitydetail', activity_id=activity_id))


@app.route('/activitycancel-<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activitycancel(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if (activity.status == CONST.ACTIVITY_SCHEDULING or activity.status == CONST.ACTIVITY_UNKNOWN) and session.get('is_arra_monitor'):
        #print Article.query.filter(Article.title==article_title).statement
        flash({'type': 'success', 'content': '活动已经取消。'})
        activity = Activity.query.get_or_404(activity_id)
        activity.status = CONST.ACTIVITY_CANCELED
        duties = Duty.query.filter(Duty.aid == activity_id)

        worktimestr = timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M")
        timestr = timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M")
        venue = venuename_filter(activity.venue)
        title = activity.title
        remark = activity.remark
        url = config.BASE_URL + url_for('activitydetail', activity_id=activity.id)
        subject = mail.activity_cancel_tmpl['subject']
        content = mail.activity_cancel_tmpl['content'] % (worktimestr, timestr, venue, title, remark, url, url)
        sms_content = sms.sms_activity_cancel_tmpl % (worktimestr, venue, title)

        notify_duties = []
        for duty in duties:
            if duty.status in [CONST.DUTY_APPLY_ING, CONST.DUTY_APPLY_CONFIRM, CONST.DUTY_ARRANGE_CONFIRM, CONST.DUTY_BEFORE_START, CONST.DUTY_REPLACE_ING]:
                notify_duties.append(duty)
            duty.status = CONST.DUTY_ACTIVITY_CANCELED
            db.session.add(duty)
        db.session.add(activity)
        db.session.commit()

        for duty in notify_duties:
            if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_ACTIVITY_CANCEL):
                msg_id = mail.send_message(duty.uid, session['uid'], subject, content, 2)
            else:
                msg_id = 0
            if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_ACTIVITY_CANCEL):
                mail.send_mail(subject, content, duty.member.name, duty.member.email, msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
            if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_ACTIVITY_CANCEL):
                pass  # TODO app notify
            if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_ACTIVITY_CANCEL):
                sms.send_sms(duty.member.mobile_num, sms_content)

    else:
        flash({'type': 'danger', 'content': '非法操作，请重试。'})
    return redirect(url_for('activitydetail', activity_id=activity_id))


@app.route('/activitystart-<int:activity_id>')
@login_required
def activitystart(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    now = int(time.time())
    if activity.status == CONST.ACTIVITY_SCHEDULING and activity.start_time <= now and session.get('is_arra_monitor'):
        #print Article.query.filter(Article.title==article_title).statement
        flash({'type': 'success', 'content': '活动已经开始。'})
        activity = Activity.query.get_or_404(activity_id)
        activity.status = CONST.ACTIVITY_ONGOING
        db.session.add(activity)
        dutylist = Duty.query.filter(Duty.aid == activity_id, or_(Duty.status == CONST.DUTY_BEFORE_START, Duty.status == CONST.DUTY_REPLACE_ING)).all()
        for duty in dutylist:
            duty.status = CONST.DUTY_ACTIVITY_ONGOING
            db.session.add(duty)
        db.session.commit()
    else:
        flash({'type': 'danger', 'content': '非法操作，请重试。'})
    return redirect(url_for('activitydetail', activity_id=activity_id))


@app.route('/activityterminate-<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activityterminate(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == CONST.ACTIVITY_ONGOING and Duty.query.filter(Duty.uid == session['uid'], Duty.aid == activity_id, Duty.status == CONST.DUTY_ACTIVITY_ONGOING).count():
        #print Article.query.filter(Article.title==article_title).statement
        last_time = int(request.form['end_time']) - activity.start_time
        if last_time < 30 * 60 or last_time > 6 * 3600:
            flash({'type': 'danger', 'content': '活动结束时间填写有误。'})
        else:
            activity.end_time = int(request.form['end_time'])
            activity.status = CONST.ACTIVITY_ENDED
            duties = Duty.query.filter(Duty.aid == activity_id, Duty.status == CONST.DUTY_ACTIVITY_ONGOING)
            for duty in duties:
                duty.status = CONST.DUTY_ACTIVITY_ENDED
                db.session.add(duty)
            db.session.add(activity)
            db.session.commit()
            flash({'type': 'success', 'content': '活动已经成功标记为结束状态。'})
    else:
        flash({'type': 'danger', 'content': '非法操作，请重试。'})
    return redirect(url_for('activitydetail', activity_id=activity_id))


@app.route('/activitysync')
@login_required
def activitysync():
    try:
        logs = sync()
        for log in logs:
            flash({'type': 'success', 'content': log})
    except Exception as e:
        flash({'type': 'danger', 'content': e})
    return redirect(url_for('activitymanage'))


@app.route('/activityjson')
@login_required
def activityjson():
    activity = Activity.query.all()
    activity_list = []
    for a in activity:
        d = {'id': a.id, 'venue': a.venue, 'start_time': a.start_time, 'end_time': a.end_time, 'type': a.type, 'title': a.title, 'remark': a.remark}
        activity_list.append(d)
    rtn = json.dumps(activity_list)
    return rtn


@app.route('/sync')
def sync():
    from acgweb.controller.spider import activity_spider
    logs = activity_spider()
    try:
        fp = open(config.BASE_DIR + 'log/sync.log', 'a')
    except:
        fp = open(config.BASE_DIR + 'log/sync.log', 'w')
    for log in logs:
        fp.write("%s\n" % log)
    fp.close()
    fp = open(config.BASE_DIR + 'data/last_sync.time', 'w')
    timestr = str(int(time.time()))
    fp.write(timestr)
    fp.close()
    return logs


# cron every half hour
@app.route('/cron')
def cron():
    try:
        last_cron = int(open(config.BASE_DIR + 'data/last_cron.time', 'r').read())
    except:
        last_cron = 0
    now = int(time.time())
    nowstr = timeformat_filter(now, "%Y-%m-%d %H:%M:%S")
    if last_cron / (30 * 60) < now / (30 * 60):
        now = now / (30 * 60) * (30 * 60)
        logs = []
        # 1 hours before activity start
        activitylist = Activity.query.filter(Activity.work_start_time == now + 3600, Activity.status == CONST.ACTIVITY_SCHEDULING).all()
        for activity in activitylist:
            work_timestr = timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M")
            timestr = timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M")
            venue = venuename_filter(activity.venue)
            title = activity.title
            remark = activity.remark
            url = config.BASE_URL + url_for('activitydetail', activity_id=activity.id)
            subject = mail.activity_nearly_begin_tmpl['subject']
            content = mail.activity_nearly_begin_tmpl['content'] % (work_timestr, timestr, venue, title, remark, url, url)
            sms_content = sms.sms_activity_nearly_begin_tmpl % (work_timestr, venue, title)
            # TODO %d or %s ?
            logs.append("%s: Activity almost start id:%d" % (nowstr, activity.id))
            for duty in activity.duties:
                #print subject, content, duty.member.name, duty.member.email, subject, content
                if duty.status == CONST.DUTY_BEFORE_START or duty.status == CONST.DUTY_REPLACE_ING:
                    if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_ACTIVITY_NEARLY_BEGIN):
                        msg_id = mail.send_message(duty.uid, config.SYS_ADMIN, subject, content, 2)
                    else:
                        msg_id = 0
                    if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_ACTIVITY_NEARLY_BEGIN):
                        mail.send_mail(subject, content, duty.member.name, duty.member.email, msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
                        logs.append("%s: Send mail to %s" % (nowstr, duty.uid))
                    if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_ACTIVITY_NEARLY_BEGIN):
                        pass  # TODO app notify
                    if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_ACTIVITY_NEARLY_BEGIN):
                        sms.send_sms(duty.member.mobile_num, sms_content)
                        logs.append("%s: Send SMS to %s" % (nowstr, duty.uid))

        # on activity start
        activitylist = Activity.query.filter(Activity.start_time == now, Activity.status == CONST.ACTIVITY_SCHEDULING).all()
        dutylist = Duty.query.join(Activity).filter(Activity.start_time == now, Activity.status == CONST.ACTIVITY_SCHEDULING, or_(Duty.status == CONST.DUTY_BEFORE_START, Duty.status == CONST.DUTY_REPLACE_ING)).all()
        for activity in activitylist:
            logs.append("%s : Activity starts, change activity status id:%d" % (nowstr, activity.id))
            activity.status = CONST.ACTIVITY_ONGOING
            db.session.add(activity)
        # TODO other duty status
        for duty in dutylist:
            logs.append("%s : Activity starts, change duty status id:%d" % (nowstr, duty.id))
            duty.status = CONST.DUTY_ACTIVITY_ONGOING
            db.session.add(duty)
        db.session.commit()

        # 6 hours after activity start

        ts = time.localtime(now)
        if ts.tm_hour == 20 and ts.tm_min == 0 and ts.tm_sec == 0:
            # auto sync
            sync()
        if ts.tm_hour == 21 and ts.tm_min == 30 and ts.tm_sec == 0:
            range_start = 86400 + now - 21 * 3600 - 1800
            range_end = 2 * 86400 + now + 2 * 3600 + 1800
            activitylist = Activity.query.filter(Activity.start_time >= range_start, Activity.start_time < range_end, Activity.status == 1).all()
            warnings = []
            for activity in activitylist:
                ready_num = 0
                for duty in activity.duties:
                    if duty.status in [CONST.DUTY_APPLY_ING, CONST.DUTY_APPLY_CONFIRM, CONST.DUTY_ARRANGE_CONFIRM, CONST.DUTY_BEFORE_START, CONST.DUTY_REPLACE_ING]:
                        ready_num += 1
                    if duty.status in [CONST.DUTY_APPLY_ING, CONST.DUTY_APPLY_CONFIRM, CONST.DUTY_ARRANGE_CONFIRM]:
                        membername = duty.member.name
                        memberurl = url_for('memberdetail', member_uid=duty.uid)
                        worktimestr = timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M")
                        timestr = timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M")
                        venue = venuename_filter(activity.venue)
                        title = activity.title
                        url = config.BASE_URL + url_for('activitydetail', activity_id=activity.id)
                        statusname = dutystatusname_filter(duty.status)
                        content = mail.todo_duty_tmpl['content'] % (memberurl, membername, worktimestr, timestr, venue, title, url, url, statusname)
                        warnings.append(content)
                if ready_num == 0:
                    worktimestr = timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M")
                    timestr = timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M")
                    venue = venuename_filter(activity.venue)
                    title = activity.title
                    url = config.BASE_URL + url_for('activitydetail', activity_id=activity.id)
                    content = mail.todo_activity_tmpl['content'] % (worktimestr, timestr, venue, title, url, url)
                    warnings.append(content)

            if warnings:
                now = int(time.time())
                nowstr = timeformat_filter(now, "%Y-%m-%d %H:%M:%S")

                subject = mail.todo_notice_tmpl['subject']
                content = mail.todo_notice_tmpl['content'] + '<hr />'.join(warnings)
                for uid in config.ARRA_MONITOR:
                    member = Member.query.get(uid)
                    if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_TODO):
                        msg_id = mail.send_message(uid, config.SYS_ADMIN, subject, content, 2)
                    else:
                        msg_id = 0
                    if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_TODO):
                        mail.send_mail(subject, content, member.name, member.email, msgid=msg_id)
                    if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_TODO):
                        pass  # TODO app notify
                    if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_TODO):
                        pass  #

        if ts.tm_hour == 22 and ts.tm_min == 30 and ts.tm_sec == 0:
            activitylist = Activity.query.filter(Activity.start_time >= now - 22 * 3600 - 1800, Activity.start_time < now + 3600 + 1800, Activity.status == CONST.ACTIVITY_ONGOING).all()
            for activity in activitylist:
                worktimestr = timeformat_filter(activity.work_start_time, "%Y-%m-%d %H:%M")
                timestr = timeformat_filter(activity.start_time, "%Y-%m-%d %H:%M")
                venue = venuename_filter(activity.venue)
                title = activity.title
                remark = activity.remark
                url = config.BASE_URL + url_for('activitydetail', activity_id=activity.id)
                subject = mail.activity_mark_endtime_tmpl['subject']
                content = mail.activity_mark_endtime_tmpl['content'] % (worktimestr, timestr, venue, title, remark, url, url)
                sms_content = sms.sms_activity_mark_endtime_tmpl % (title)
                logs.append("%s : Activity almost end id:%d" % (nowstr, activity.id))
                for duty in activity.duties:
                    if duty.status == CONST.DUTY_ACTIVITY_ONGOING:
                        #print subject, content
                        if notify.is_notify(duty.uid, notify.NOTIFY_MESSAGE, notify.NOTIFY_ACTIVITY_MARK_ENDTIME):
                            msg_id = mail.send_message(duty.uid, config.SYS_ADMIN, subject, content, 2)
                        else:
                            msg_id = 0
                        if notify.is_notify(duty.uid, notify.NOTIFY_EMAIL, notify.NOTIFY_ACTIVITY_MARK_ENDTIME):
                            mail.send_mail(subject, content, duty.member.name, duty.member.email, msgid=msg_id, touid=duty.uid, uid=duty.uid, dutyid=duty.id, activityid=duty.aid)
                            logs.append("%s: Send mail to %s" % (nowstr, duty.uid))
                        if notify.is_notify(duty.uid, notify.NOTIFY_APP, notify.NOTIFY_ACTIVITY_MARK_ENDTIME):
                            pass  # TODO app notify
                        if notify.is_notify(duty.uid, notify.NOTIFY_SMS, notify.NOTIFY_ACTIVITY_MARK_ENDTIME):
                            sms.send_sms(duty.member.mobile_num, sms_content)
                            logs.append("%s: Send SMS to %s" % (nowstr, duty.uid))

                        logs.append("%s : Send mail to %s" % (nowstr, duty.uid))

        open(config.BASE_DIR + 'data/last_cron.time', 'w').write(str(now))

        try:
            fp = open(config.BASE_DIR + 'log/cron.log', 'a')
        except:
            fp = open(config.BASE_DIR + 'log/cron.log', 'w')
        fp.write("crontab %s : %d\n" % (nowstr, now))
        for log in logs:
            fp.write("%s\n" % log)
        fp.close()

        return "now" + str(now)
    else:
        try:
            fp = open(config.BASE_DIR + 'log/cron.log', 'a')
        except:
            fp = open(config.BASE_DIR + 'log/cron.log', 'w')
        fp.write("crontab_last %s : %d\n" % (nowstr, now))
        fp.close()
        return "last_cron" + str(last_cron)
