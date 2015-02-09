# coding: utf-8

import jpush as jpush
from acgweb import config


def push_alias(uid, message, **kargs):
    _jpush = jpush.JPush(config.JPUSH_APPKEY, config.JPUSH_SECRET)
    push = _jpush.create_push()
    push.audience = jpush.audience(jpush.alias(uid))
    #push.options
    android = jpush.android(alert=message, extras=kargs)
    push.notification = jpush.notification(android=android)
    push.platform = jpush.all_
    try:
        resp = push.send()
        success = True
    except jpush.JPushFailure:
        resp = 'JPushFailure %s %s' % (uid, message)
        success = False
    try:
        fp = open(config.BASE_DIR + 'log/push.log', 'a')
    except:
        fp = open(config.BASE_DIR + 'log/push.log', 'w')

    fp.write("%s\n" % resp)
    fp.close()
    return success
