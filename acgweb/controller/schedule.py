# coding: utf-8
import time

from flask import render_template, json, abort, flash, make_response
from acgweb import app, db
from acgweb.model.schedule import Schedule
from acgweb.model.member import Member
from acgweb.form.schedule import ScheduleForm
import acgweb.const as CONST
from acgweb import config
from decorated_function import *


@app.route('/myschedule')
@login_required
def myschedule():
    """Page: all activitylist"""
    schedule_list = Schedule.query.filter(Schedule.uid == session[u'uid'], Schedule.semester == config.SEMESTER).all()
    if viewtype() == 1:
        return render_template('schedule/schedulelist_mobile.html',
            schedule_list=schedule_list,)
    else:
        return render_template('schedule/schedulelist.html',
            schedule_list=schedule_list,)


@app.route('/myschedule')
@login_required
def myscheduleapi():
    uid = request.args.get('uid')
    schedule_list = Schedule.query.filter(Schedule.uid == uid, Schedule.semester == config.SEMESTER).all()
    res = []
    for schedule in schedule_list:
        d = {}
        d['id'] = schedule.id
        d['classname'] = schedule.classname
        d['classtype'] = schedule.classtype
        d['week'] = schedule.week
        d['weekday'] = schedule.weekday
        d['section'] = schedule.section
        res.append(d)
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/schedulemanage-p<int:pagenum>')
@app.route('/schedulemanage')
@login_required
def schedulemanage(pagenum=1):
    """Page: all activitylist"""
    schedule_count = Schedule.query.filter(Schedule.semester == config.SEMESTER).count()
    schedule_list = Schedule.query.filter(Schedule.semester == config.SEMESTER).limit(CONST.schedule_per_page).offset(CONST.schedule_per_page * (pagenum - 1))
    return render_template('schedule/schedulemanage.html',
        schedule_list=schedule_list, page_count=(schedule_count - 1) / CONST.message_per_page + 1, page_current=pagenum)


@app.route('/update_all_schedule_cache')
@login_required
def update_all_schedule_cache():
    update_schedule_cache()
    update_schedule_cache('empty')
    return redirect(url_for('manage'))


def update_schedule_cache(uid=''):
    if uid == '':
        member_list = Member.query.all()
        uidlist = [i.uid for i in member_list]
    else:
        uidlist = [uid]

    for uid in uidlist:
        schedule_list = Schedule.query.filter(Schedule.uid == uid, Schedule.semester == config.SEMESTER).all()
        fp = open(config.BASE_DIR + 'cache/st_%s.log' % uid, 'w')
        schedule_table = {}
        for i in range(1, 27):
            for j in range(7):
                dayint = config.SEMESTER_BASE + ((i - 1) * 7 + j) * 86400
                daystr = time.strftime('%Y-%m-%d', time.localtime(dayint))
                if not schedule_table.has_key(daystr):
                    schedule_table[daystr] = {}
                for k in range(1, 13):
                    if not schedule_table[daystr].has_key(k):
                        schedule_table[daystr][k] = []

        for sch in schedule_list:
            sch.strtolist()
            for week in sch.weeklist:
                for weekday in sch.weekdaylist:
                    dayint = config.SEMESTER_BASE + ((week - 1) * 7 + weekday) * 86400
                    daystr = time.strftime('%Y-%m-%d', time.localtime(dayint))
                    for section in sch.sectionlist:
                        schedule_table[daystr][section].append(sch.classname)

        keys = schedule_table.keys()
        #print keys
        keys.sort()
        #print keys
        for daystr in keys:
            content = daystr
            for i in range(1, 13):
                content += '\t' + ('.'.join(schedule_table[daystr][i]))
            fp.write(content + '\n')
        fp.close()


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
            schedule.uid = session[u'uid']
            schedule.week = form.week.data
            schedule.weekday = form.weekday.data
            schedule.section = form.section.data
            schedule.classname = form.classname.data
            schedule.classtype = form.classtype.data
            schedule.update_semester()
            db.session.add(schedule)
            db.session.commit()

            flash({'type': 'success', 'content': '保存成功！'})
            update_schedule_cache(session[u'uid'])
            return redirect('/myschedule')
        if viewtype() == 1:
            return render_template('schedule/schedule-form_mobile.html', form=form)
        else:
            return render_template('schedule/schedule-form.html', form=form)
    else:
        if schedule_id:
            schedule = Schedule.query.get_or_404(schedule_id)
            if schedule.uid != session[u'uid']:
                abort(403)
            form = ScheduleForm(obj=schedule)
        else:
            form = ScheduleForm()
        if viewtype() == 1:
            return render_template('schedule/schedule-form_mobile.html', form=form)
        else:
            return render_template('schedule/schedule-form.html', form=form)


@app.route('/myschedule_delete-<int:schedule_id>')
@login_required
def myschedule_delete(schedule_id):
    schedule = Schedule.query.get(schedule_id)
    if schedule.uid != session[u'uid']:
        abort(403)
    flash({'type': 'success', 'content': '课表已删除。'})
    db.session.delete(schedule)
    db.session.commit()
    update_schedule_cache(session[u'uid'])
    return redirect(url_for('myschedule'))
