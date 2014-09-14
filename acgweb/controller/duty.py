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
    activity_list = Activity.query.filter(Activity.end_time != 0).order_by('start_time DESC').limit(CONST.duty_per_page).offset(CONST.duty_per_page*(pagenum-1))

    if viewtype()==1:
        return render_template('duty/dutylist_mobile.html',
            activity_list=activity_list,
            page_count=(activity_count-1)/CONST.duty_per_page+1,page_current=pagenum)
    else:
        return render_template('duty/dutylist.html',
            activity_list=activity_list,
            page_count=(activity_count-1)/CONST.duty_per_page+1,page_current=pagenum)


@app.route('/api/dutylist')
#@login_required
def dutylistapi():
    activity_list = Activity.query.filter(Activity.end_time != 0).order_by('start_time DESC').limit(50)
    res = []
    for activity in activity_list:
        d = {}
        d['id'] = activity.id
        d['title'] = activity.title
        d['start_time'] = activity.start_time
        d['work_start_time'] = activity.work_start_time
        d['venue'] = activity.venue
        d['end_time'] = activity.end_time
        d['logs'] = []
        for duty in activity.duties:
            for log in duty.getlogs():
                d['logs'].append({'uid': duty.member.uid, 'name': duty.member.name, 'type': log['type'], 'content': log['content']})
        res.append(d)
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/dutymanage-p<int:pagenum>')
@app.route('/dutymanage')
@login_required
def dutymanage(pagenum=1):
    """Page: all activitylist"""
    ts = time.localtime()
    todaytime = int(time.time()) - ts.tm_hour*3600 - ts.tm_min*60 - ts.tm_sec
    #config.SEMASTER_BASE

    duty_count = Duty.query.join(Activity).filter(Activity.start_time >= todaytime-3*86400).count()
    duty_list = Duty.query.join(Activity).filter(Activity.start_time >= todaytime-3*86400)\
        .order_by(Activity.start_time).limit(CONST.dutylist_per_page).offset(CONST.dutylist_per_page*(pagenum-1))

    return render_template('duty/dutymanage.html',
        duty_list=duty_list,
        page_count=(duty_count-1)/CONST.dutylist_per_page+1,page_current=pagenum)


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
            duty.aid=form.aid.data
            duty.uid=form.uid.data
            duty.status=form.status.data
            #duty.process=form.process.data
            #duty.log=form.log.data
            db.session.add(duty)
            db.session.commit()

            flash({'type':'success', 'content':'保存成功！'})
            return redirect(url_for('dutyedit',duty_id=duty_id))
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

    flash({'type':'success', 'content':'删除成功！'})
    return redirect('/dutymanage')


