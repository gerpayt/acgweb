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

default_setting = {
    NOTIFY_ACTIVITY_APPOINT       : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_ACTIVITY_MODIFY        : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_ACTIVITY_CANCEL        : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_APPROVE_APPLY          : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_DECLINE_APPLY          : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_COVER_DUTY             : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_ACTIVITY_NEARLY_BEGIN  : { NOTIFY_MESSAGE: 0, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_ACTIVITY_MARK_ENDTIME  : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_DECLINE_DUTY           : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_SPIDER                 : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 0, NOTIFY_SMS: 0},
    NOTIFY_TODO                   : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_ERROR                  : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_OTHER                  : { NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0}
}


def is_notify(uid, event, method):
    member = Member.query.get_or_404(uid)
    setting = json.loads(member.json)
    setting = default_setting.update(setting)
    return setting[event][method]
