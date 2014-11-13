# coding: utf-8

from flask import render_template, json, flash, jsonify, abort, make_response
from acgweb import db
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from acgweb import config
from template_filter import *
from decorated_function import *


activity_train_set = None


@app.route('/activity_operations')
@login_required
def activity_operations():
    accept_duty_list = []
    decline_duty_list = []
    confirm_apply_list = []
    member_list = {}

    start_time = time.time() - 30 * 86400
    duty_list = Duty.query.join(Activity).filter(Activity.start_time >= start_time).\
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
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'interval': item['time'] - approve_apply_time}
                confirm_apply_list.append(tmp_dict)
            elif item['op'] == 'accept_duty':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'interval': item['time'] - activity_appoint_time}
                accept_duty_list.append(tmp_dict)
                member_list[duty.uid]['activity_appoint']['accept'] += 1
            elif item['op'] == 'decline_duty':
                tmp_dict = {'activity': duty.activity, 'member': duty.member, 'time': item['time'],
                            'content': item['content'], 'interval': item['time'] - activity_appoint_time}
                decline_duty_list.append(tmp_dict)
                member_list[duty.uid]['activity_appoint']['decline'] += 1
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


    member_list = sorted(member_list.values(), key=lambda e: e['activity_source']['total'], reverse=True)

    return render_template('activity/activity_operations.html', decline_duty_list=decline_duty_list, accept_duty_list=accept_duty_list,
                           confirm_apply_list=confirm_apply_list, member_list=member_list)