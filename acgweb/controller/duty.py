# coding: utf-8
from flask import render_template, request, redirect, url_for, json
from acgweb import app, db
from acgweb.model.activity import Activity
import template_filter
from decorated_function import *
import acgweb.const as CONST

@app.route('/dutylist-p<int:pagenum>')
@app.route('/dutylist-v<vid>-p<int:pagenum>')
@app.route('/dutylist-v<vid>')
@app.route('/dutylist')
@login_required
def dutylist(pagenum=1,vid=''):
    """Page: all activitylist"""
    activity_count = Activity.query.filter(Activity.end_time != 0).count()
    activity_list = Activity.query.filter(Activity.end_time != 0).order_by('start_time DESC').limit(CONST.duty_per_page).offset(CONST.duty_per_page*(pagenum-1))

    return render_template('duty/dutylist.html',
        activity_list=activity_list,
        page_count=(activity_count-1)/CONST.duty_per_page+1,page_current=pagenum)


