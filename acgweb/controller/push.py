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
    push.send()
