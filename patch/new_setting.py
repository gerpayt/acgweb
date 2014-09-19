# -- coding:utf-8 --
import sys
sys.path.append("../acgweb")

import json
from acgweb.controller.notify import *

'''
data = {
    NOTIFY_ACTIVITY_APPOINT       : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_ACTIVITY_MODIFY        : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_ACTIVITY_CANCEL        : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_APPROVE_APPLY          : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_DECLINE_APPLY          : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_COVER_DUTY             : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_ACTIVITY_NEARLY_BEGIN  : {NOTIFY_MESSAGE: 0, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 1},
    NOTIFY_ACTIVITY_MARK_ENDTIME  : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_DECLINE_DUTY           : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_SPIDER                 : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 0, NOTIFY_SMS: 0},
    NOTIFY_TODO                   : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_ERROR                  : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0},
    NOTIFY_OTHER                  : {NOTIFY_MESSAGE: 1, NOTIFY_EMAIL: 1, NOTIFY_APP: 1, NOTIFY_SMS: 0}
}
'''

data = {
    '1-1': 1, '1-2': 1, '1-3': 1, '1-4': 1,
    '2-1': 1, '2-2': 1, '2-3': 1, '2-4': 0,
    '3-1': 1, '3-2': 1, '3-3': 1, '3-4': 0,
    '4-1': 1, '4-2': 1, '4-3': 1, '4-4': 1,
    '5-1': 1, '5-2': 1, '5-3': 1, '5-4': 1,
    '6-1': 1, '6-2': 1, '6-3': 1, '6-4': 1,
    '7-1': 0, '7-2': 1, '7-3': 1, '7-4': 1,
    '8-1': 1, '8-2': 1, '8-3': 1, '8-4': 0,
    '9-1': 1, '9-2': 1, '9-3': 1, '9-4': 0,
    '10-1': 1, '10-2': 1, '10-3': 1, '10-4': 0,
    '11-1': 1, '11-2': 1, '11-3': 1, '11-4': 0,
    '12-1': 1, '12-2': 1, '12-3': 1, '12-4': 0,
    '13-1': 1, '13-2': 1, '13-3': 1, '13-4': 0
}

print json.dumps(data)
