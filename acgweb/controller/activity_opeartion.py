# coding: utf-8

from flask import render_template, json, flash, jsonify, abort, make_response
from acgweb import db
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from acgweb import config
from template_filter import *
from decorated_function import *


activity_train_set = None


@app.route('/activity_opeartions')
@login_required
def activity_opeartions():
    accept_duty_list = []
    decline_duty_list = []
    confirm_apply_list = []

    start_time = time.time() - 30 * 86400
    duty_list = Duty.query.join(Activity).filter(Activity.start_time >= start_time).order_by(Activity.start_time.desc())
    for duty in duty_list:
        activity_appoint_time = 0
        approve_apply_time = 0
        for item in duty.getprocesses():
            if item['op'] == 'activity_appoint':
                activity_appoint_time = item['time']
            elif item['op'] == 'approve_apply':
                approve_apply_time = item['time']
            elif item['op'] == 'decline_duty':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'content': item['content'], 'interval': item['time'] - activity_appoint_time}
                decline_duty_list.append(tmp_dict)
            elif item['op'] == 'accept_duty':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'interval': item['time'] - activity_appoint_time}
                accept_duty_list.append(tmp_dict)
            elif item['op'] == 'confirm_apply':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'interval': item['time'] - approve_apply_time}
                confirm_apply_list.append(tmp_dict)
    return render_template('activity/activity_opeartions.html', decline_duty_list=decline_duty_list, accept_duty_list=accept_duty_list,
                           confirm_apply_list=confirm_apply_list)