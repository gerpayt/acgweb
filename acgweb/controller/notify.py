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
NOTIFY_NOTICE_ACTIVITY_MODIFY = 10
NOTIFY_NOTICE_ACTIVITY_CANCEL = 11
NOTIFY_TODO = 12
NOTIFY_ERROR = 13
NOTIFY_OTHER = 14


