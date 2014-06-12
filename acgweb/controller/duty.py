# coding: utf-8
from flask import render_template, request, redirect, url_for, json
from acgweb import app, db
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
import template_filter
from decorated_function import *
import acgweb.const as CONST

@app.route('/dutylist-p<int:pagenum>')
@app.route('/dutylist')
@login_required
def dutylist(pagenum=1):
    """Page: all activitylist"""
    activity_count = Activity.query.filter(Activity.end_time != 0).count()
    activity_list = Activity.query.filter(Activity.end_time != 0).order_by('start_time DESC').limit(CONST.duty_per_page).offset(CONST.duty_per_page*(pagenum-1))

    return render_template('duty/dutylist.html',
        activity_list=activity_list,
        page_count=(activity_count-1)/CONST.duty_per_page+1,page_current=pagenum)

@app.route('/dutymanage-p<int:pagenum>')
@app.route('/dutymanage')
@login_required
def dutymanage(pagenum=1):
    """Page: all activitylist"""
    duty_count = Duty.query.count()
    duty_list = Duty.query.join(Activity).order_by(Activity.start_time).limit(CONST.dutylist_per_page).offset(CONST.dutylist_per_page*(pagenum-1))

    return render_template('duty/dutymanage.html',
        duty_list=duty_list,
        page_count=(duty_count-1)/CONST.dutylist_per_page+1,page_current=pagenum)


@app.route('/dutyedit-<int:duty_id>')
@login_required
def dutyedit(duty_id):
    """Page: all activitylist"""
    duty = Duty.query.get_or_404(duty_id)

    return render_template('duty/dutyedit.html',
        duty=duty,)


