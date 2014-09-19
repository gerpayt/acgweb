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

NOTIFY_ACTIVITY_APPOINT = 1
NOTIFY_ACTIVITY_MODIFY = 2
NOTIFY_ACTIVITY_CANCEL = 3
NOTIFY_APPROVE_APPLY = 4
NOTIFY_DECLINE_APPLY = 5
NOTIFY_COVER_DUTY = 6
NOTIFY_ACTIVITY_NEARLY_BEGIN = 7
NOTIFY_ACTIVITY_MARK_ENDTIME = 8
NOTIFY_DECLINE_DUTY = 9
NOTIFY_SPIDER = 10
NOTIFY_TODO = 11
NOTIFY_ERROR = 12
NOTIFY_OTHER = 13

NOTIFY_MESSAGE = 1
NOTIFY_EMAIL = 2
NOTIFY_APP = 3
NOTIFY_SMS = 4

notify_setting_list = ['排班提醒', '活动信息变更提醒', '活动取消提醒', '申请排班批准提醒', '申请排班拒绝提醒', '被成功代班提醒', '值班前一小时提醒', '标记活动结束时间提醒',
                       '[班长]拒绝值班提醒', '[班长]自动同步完成提醒', '[班长]近期未完成操作提醒', '[班长]系统内部错误', '[班长]其他通知提醒']


default_setting = {
    '1-1': 1, '1-2': 1, '1-3': 1, '1-4': 0,
    '2-1': 1, '2-2': 1, '2-3': 1, '2-4': 0,
    '3-1': 1, '3-2': 1, '3-3': 1, '3-4': 0,
    '4-1': 1, '4-2': 1, '4-3': 1, '4-4': 0,
    '5-1': 1, '5-2': 1, '5-3': 1, '5-4': 0,
    '6-1': 1, '6-2': 1, '6-3': 1, '6-4': 0,
    '7-1': 0, '7-2': 1, '7-3': 1, '7-4': 0,
    '8-1': 1, '8-2': 1, '8-3': 1, '8-4': 0,
    '9-1': 1, '9-2': 1, '9-3': 1, '9-4': 0,
    '10-1': 1, '10-2': 1, '10-3': 1, '10-4': 0,
    '11-1': 1, '11-2': 1, '11-3': 1, '11-4': 0,
    '12-1': 1, '12-2': 1, '12-3': 1, '12-4': 0,
    '13-1': 1, '13-2': 1, '13-3': 1, '13-4': 0
}

empty_setting = {
    '1-1': 0, '1-2': 0, '1-3': 0, '1-4': 0,
    '2-1': 0, '2-2': 0, '2-3': 0, '2-4': 0,
    '3-1': 0, '3-2': 0, '3-3': 0, '3-4': 0,
    '4-1': 0, '4-2': 0, '4-3': 0, '4-4': 0,
    '5-1': 0, '5-2': 0, '5-3': 0, '5-4': 0,
    '6-1': 0, '6-2': 0, '6-3': 0, '6-4': 0,
    '7-1': 0, '7-2': 0, '7-3': 0, '7-4': 0,
    '8-1': 0, '8-2': 0, '8-3': 0, '8-4': 0,
    '9-1': 0, '9-2': 0, '9-3': 0, '9-4': 0,
    '10-1': 0, '10-2': 0, '10-3': 0, '10-4': 0,
    '11-1': 0, '11-2': 0, '11-3': 0, '11-4': 0,
    '12-1': 0, '12-2': 0, '12-3': 0, '12-4': 0,
    '13-1': 0, '13-2': 0, '13-3': 0, '13-4': 0
}


def is_notify(uid, method, event):
    member = Member.query.get_or_404(uid)
    setting = default_setting.copy()
    if member.setting != '':
        setting.update(json.loads(member.setting))
    #print uid, event, method, setting[str(event)+'-'+str(method)]
    return setting[str(event)+'-'+str(method)]
