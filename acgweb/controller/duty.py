# coding: utf-8
import time

from flask import render_template, json, abort, flash, make_response
from acgweb import app, db
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from acgweb.form.duty import DutyForm
from decorated_function import *
import acgweb.const as CONST


@app.route('/dutylist-p<int:pagenum>')
@app.route('/dutylist')
@login_required
def dutylist(pagenum=1):
    """Page: all activitylist"""
    activity_count = Activity.query.filter(Activity.end_time != 0).count()
    activity_list = Activity.query.filter(Activity.end_time != 0).order_by('start_time DESC').limit(CONST.duty_per_page).offset(CONST.duty_per_page * (pagenum - 1))

    if viewtype() == 1:
        return render_template('duty/dutylist_mobile.html',
            activity_list=activity_list,
            page_count=(activity_count - 1) / CONST.duty_per_page + 1, page_current=pagenum)
    else:
        return render_template('duty/dutylist.html',
            activity_list=activity_list,
            page_count=(activity_count - 1) / CONST.duty_per_page + 1, page_current=pagenum)


@app.route('/api/dutylist')
@return_json
def dutylistapi(me):
    pagenum = int(request.args.get('pagenum', 1))
    activity_list = Activity.query.filter(Activity.end_time != 0).order_by('start_time DESC').limit(CONST.duty_per_page).offset(CONST.duty_per_page * (pagenum - 1))
    res = []
    for activity in activity_list:
        d = {}
        d['id'] = activity.id
        d['title'] = activity.title
        d['venue'] = activity.venue
        d['work_start_time'] = activity.work_start_time
        d['start_time'] = activity.start_time
        d['end_time'] = activity.end_time
        d['type'] = activity.type
        d['status'] = activity.status
        d['logs'] = []
        for duty in activity.duties:
            for log in duty.getlogs():
                d['logs'].append({'uid': duty.member.uid, 'name': duty.member.name, 'type': log['type'], 'content': log['content']})
        res.append(d)
    return res


@app.route('/dutymanage-p<int:pagenum>')
@app.route('/dutymanage')
@login_required
def dutymanage(pagenum=1):
    """Page: all activitylist"""
    ts = time.localtime()
    todaytime = int(time.time()) - ts.tm_hour * 3600 - ts.tm_min * 60 - ts.tm_sec
    #config.SEMESTER_BASE

    duty_count = Duty.query.join(Activity).filter(Activity.start_time >= todaytime - 3 * 86400).count()
    duty_list = Duty.query.join(Activity).filter(Activity.start_time >= todaytime - 3 * 86400)\
        .order_by(Activity.start_time).limit(CONST.dutylist_per_page).offset(CONST.dutylist_per_page * (pagenum - 1))

    return render_template('duty/dutymanage.html',
        duty_list=duty_list,
        page_count=(duty_count - 1) / CONST.dutylist_per_page + 1, page_current=pagenum)


@app.route('/dutyedit-<int:duty_id>', methods=['GET', 'POST'])
@login_required
def dutyedit(duty_id):
    """Page: all activitylist"""
    if request.method == 'POST':
        form = DutyForm(request.form)
        duty = Duty.query.get(form.id.data)
        if form.validate_on_submit():
            if not form.errors:
                pass#form.username.errors.append('帐号已存在')
        #print form.errors
        if not form.errors:
            if not session.get('is_arra_monitor'):
                abort(403)
            duty.aid = form.aid.data
            duty.uid = form.uid.data
            duty.status = form.status.data
            #duty.process=form.process.data
            #duty.log=form.log.data
            db.session.add(duty)
            db.session.commit()

            flash({'type': 'success', 'content': '保存成功！'})
            return redirect(url_for('dutyedit', duty_id=duty_id))
        return render_template('duty/dutyedit.html', form=form, duty=duty)

    else:
        duty = Duty.query.get_or_404(duty_id)
        if not session.get('is_arra_monitor'):
            abort(403)
        #print duty
        form = DutyForm(obj=duty)
        #print form
        return render_template('duty/dutyedit.html', form=form, duty=duty)


@app.route('/dutydelete-<int:duty_id>')
@login_required
def dutydelete(duty_id):
    """Page: all activitylist"""
    duty = Duty.query.get(duty_id)
    if not session.get('is_arra_monitor'):
        abort(403)
    db.session.delete(duty)
    db.session.commit()

    flash({'type': 'success', 'content': '删除成功！'})
    return redirect('/dutymanage')


@app.route('/duty_stat')
@login_required
def duty_stat():
    member_list = {}

    end_time = time.time()
    start_time = time.time() - 30 * 86400
    duty_list = Duty.query.join(Activity).filter(Activity.start_time >= start_time, Activity.start_time < end_time).\
        order_by(Activity.start_time.desc())
    for duty in duty_list:
        activity_appoint_time = 0
        approve_apply_time = 0
        if duty.uid not in member_list:
            member_list[duty.uid] = {'uid': duty.uid, 'name': duty.member.name}
            member_list[duty.uid]['activity_source'] = {'apply': 0, 'appoint': 0, 'cover': 0}
            member_list[duty.uid]['activity_apply'] = {'approve': 0, 'decline': 0, 'cancel': 0, 'other': 0}
            member_list[duty.uid]['activity_appoint'] = {'accept': 0, 'decline': 0, 'cancel': 0, 'other': 0}
            member_list[duty.uid]['activity_term'] = {'success': 0, 'cover': 0, 'decline': 0, 'cancel': 0, 'other': 0}

            member_list[duty.uid]['operation_interval'] = []

        step = 0
        for item in duty.getprocesses():
            step += 1
            if item['op'] == 'activity_appoint':
                member_list[duty.uid]['activity_source']['appoint'] += 1
                activity_appoint_time = item['time']
            elif item['op'] == 'apply_duty':
                member_list[duty.uid]['activity_source']['apply'] += 1
            elif item['op'] == 'approve_apply':
                approve_apply_time = item['time']
                member_list[duty.uid]['activity_apply']['approve'] += 1
            elif item['op'] == 'decline_apply':
                approve_apply_time = item['time']
                member_list[duty.uid]['activity_apply']['approve'] += 1
            elif item['op'] == 'confirm_apply':
                member_list[duty.uid]['operation_interval'].append(item['time'] - approve_apply_time)
            elif item['op'] == 'accept_duty':
                member_list[duty.uid]['activity_appoint']['accept'] += 1
                member_list[duty.uid]['operation_interval'].append(item['time'] - activity_appoint_time)
            elif item['op'] == 'decline_duty':
                member_list[duty.uid]['activity_appoint']['decline'] += 1
                member_list[duty.uid]['operation_interval'].append(item['time'] - activity_appoint_time)
            elif item['op'] == 'cover_duty' and step == 1:
                member_list[duty.uid]['activity_source']['cover'] += 1
            elif item['op'] == 'cancel_task':
                member_list[duty.uid]['activity_appoint']['cancel'] += 1
                member_list[duty.uid]['activity_term']['cancel'] += 1
            elif item['op'] == 'cancel_apply':
                member_list[duty.uid]['activity_apply']['cancel'] += 1
                member_list[duty.uid]['activity_term']['cancel'] += 1

        if duty.status == CONST.DUTY_ACTIVITY_ENDED:
            member_list[duty.uid]['activity_term']['success'] += 1
        elif duty.status == CONST.DUTY_REPLACE_ED:
            member_list[duty.uid]['activity_term']['cover'] += 1
        elif duty.status == CONST.DUTY_ACTIVITY_CANCELED:
            member_list[duty.uid]['activity_term']['cancel'] += 1

    for member in member_list:
        member_list[member]['activity_source']['total'] = sum(member_list[member]['activity_source'].values())

        member_list[member]['activity_term']['decline'] = member_list[member]['activity_apply']['decline'] +\
                                                           member_list[member]['activity_appoint']['decline']

        member_list[member]['activity_apply']['other'] = member_list[member]['activity_source']['apply'] -\
                                                           member_list[member]['activity_apply']['approve'] -\
                                                           member_list[member]['activity_apply']['decline'] -\
                                                           member_list[member]['activity_apply']['cancel']
        member_list[member]['activity_appoint']['other'] = member_list[member]['activity_source']['appoint'] -\
                                                           member_list[member]['activity_appoint']['accept'] -\
                                                           member_list[member]['activity_appoint']['decline'] -\
                                                           member_list[member]['activity_appoint']['cancel']
        member_list[member]['activity_term']['other'] = member_list[member]['activity_source']['total'] -\
                                                           member_list[member]['activity_term']['success'] -\
                                                           member_list[member]['activity_term']['cover'] -\
                                                           member_list[member]['activity_term']['decline'] -\
                                                           member_list[member]['activity_term']['cancel']

        member_list[member]['activity_apply']['total'] = sum(member_list[member]['activity_apply'].values())
        member_list[member]['activity_appoint']['total'] = sum(member_list[member]['activity_appoint'].values())
        member_list[member]['activity_term']['total'] = sum(member_list[member]['activity_term'].values())

        #member_list[member]['operation_interval_average'] = sum(member_list[member]['operation_interval']) /\
        #                                                    len(member_list[member]['operation_interval'])

        if len(member_list[member]['operation_interval']) == 0:
            member_list[member]['operation_interval_middle'] = 0
        else:
            member_list[member]['operation_interval_middle'] = sorted(member_list[member]['operation_interval'])[len(member_list[member]['operation_interval'])/2]

    member_list = sorted(member_list.values(), key=lambda e: e['activity_source']['total'], reverse=True)

    return render_template('duty/duty_stat.html', member_list=member_list)


@app.route('/decline_reason')
@login_required
def decline_reason():
    decline_duty_list = []

    end_time = time.time()
    start_time = time.time() - 30 * 86400
    duty_list = Duty.query.join(Activity).filter(Activity.start_time >= start_time).order_by(Activity.start_time.desc())
    for duty in duty_list:
        activity_appoint_time = 0
        step = 0
        for item in duty.getprocesses():
            step += 1
            if item['op'] == 'activity_appoint':
                activity_appoint_time = item['time']
            elif item['op'] == 'decline_duty':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'content': item['content'], 'interval': item['time'] - activity_appoint_time}
                decline_duty_list.append(tmp_dict)

    decline_duty_list = sorted(decline_duty_list, key=lambda e: e['time'], reverse=True)

    return render_template('duty/decline_reason.html', decline_duty_list=decline_duty_list)


@app.route('/operation_interval')
@login_required
def operation_interval():
    operation_list = []

    end_time = time.time()
    start_time = time.time() - 30 * 86400
    duty_list = Duty.query.join(Activity).filter(Activity.start_time >= start_time).order_by(Activity.start_time.desc())
    for duty in duty_list:
        activity_appoint_time = 0
        approve_apply_time = 0

        step = 0
        for item in duty.getprocesses():
            step += 1
            if item['op'] == 'activity_appoint':
                activity_appoint_time = item['time']
            elif item['op'] == 'approve_apply':
                approve_apply_time = item['time']
            elif item['op'] == 'decline_apply':
                approve_apply_time = item['time']
            elif item['op'] == 'confirm_apply':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'interval': item['time'] - approve_apply_time, 'type': 'confirm'}
                operation_list.append(tmp_dict)
            elif item['op'] == 'accept_duty':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'interval': item['time'] - activity_appoint_time, 'type': 'accept'}
                operation_list.append(tmp_dict)
            elif item['op'] == 'decline_duty':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'interval': item['time'] - activity_appoint_time, 'type': 'decline'}
                operation_list.append(tmp_dict)

    operation_list = sorted(operation_list, key=lambda e: e['time'], reverse=True)

    return render_template('duty/operation_interval.html', operation_list=operation_list)
