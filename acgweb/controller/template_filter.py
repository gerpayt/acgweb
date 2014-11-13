# coding: utf-8
from acgweb import app
import acgweb.const as CONST


@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]


@app.template_filter('substr')
def substr_filter(s, a, b):
    return s[a:b]

import time


@app.template_filter('timeformat')
def timeformat_filter(t, formatstr):
    return time.strftime(formatstr, time.localtime(int(t)))


@app.template_filter('friendlytime')
def friendlytime_filter(t):
    gap = int(time.time() - t)
    if gap > 10 * 365 * 24 * 60 * 60:
        return "很久之前"
    year, mon = divmod(gap,  365 * 24 * 60 * 60)
    mon, day = divmod(mon,  30 * 24 * 60 * 60)
    day, hour = divmod(day,  24 * 60 * 60)
    hour, min = divmod(hour, 60 * 60)
    min, sec = divmod(min,  60)

    if year: rtnstr = str(year) + '年前'
    elif mon: rtnstr = str(mon) + '月前'
    elif day: rtnstr = str(day) + '日前'
    elif hour: rtnstr = str(hour) + '小时前'
    elif min: rtnstr = str(min) + '分钟前'
    elif sec: rtnstr = str(sec) + '秒前'
    else: rtnstr = '刚刚'
    #rtnstr += ''
    return rtnstr


@app.template_filter('dayname')
def dayname_filter(t):
    days = ['一', '二', '三', '四', '五', '六', '日']
    return '星期' + days[time.localtime(int(t)).tm_wday]


@app.template_filter('monthname')
def monthname_filter(t):
    months = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
    return months[time.localtime(int(t)).tm_mon] + '月'


@app.template_filter('periodname')
def periodname_filter(t):
    p = time.localtime(int(t)).tm_hour
    if p < 12: perstr = '上午'
    elif p < 17: perstr = '下午'
    else: perstr = '晚上'
    return perstr


@app.template_filter('venuename')
def venuename_filter(v):
    return CONST.venuename[v]


@app.template_filter('venuecolor')
def venuecolor_filter(v):
    return CONST.venuecolor[v]


@app.template_filter('activitytypename')
def activitytypename_filter(t):
    return CONST.activitytypename[t]


@app.template_filter('activitytypecolor')
def activitytypecolor_filter(t):
    return CONST.activitytypecolor[t]


@app.template_filter('activitystatuscolor')
def activitystatuscolor_filter(t):
    return CONST.activitystatuscolor[t]


@app.template_filter('activitystatusname')
def activitystatusname_filter(t):
    return CONST.activitystatusname[t]


@app.template_filter('dutystatusname')
def dutystatusname_filter(t):
    return CONST.dutystatusname[t]


@app.template_filter('dutystatuscolor')
def dutystatuscolor_filter(t):
    return CONST.dutystatuscolor[t]


@app.template_filter('classtypename')
def classtypename_filter(t):
    return CONST.classtypename[t]


@app.template_filter('dutyoperationname')
def dutyoperationname_filter(t):
    return CONST.dutyoperationname[t]


@app.template_filter('sexname')
def sexname_filter(t):
    return CONST.sexname[t]


@app.template_filter('mobiletypename')
def mobiletypename_filter(t):
    return CONST.mobiletypename[t]


@app.template_filter('dutylogtypename')
def dutylogtypename_filter(t):
    return CONST.dutylogtypename[t]


@app.template_filter('categoryname')
def categoryname(t):
    return CONST.categoryname[t]


@app.template_filter('messagetypename')
def messagetypename(t):
    return CONST.messagetypename[t]


@app.template_filter('membertypename')
def membertypename(t):
    return CONST.membertypename[t]


@app.template_filter('intervaltime')
def intervaltime(t):
    if t > 10 * 365 * 24 * 60 * 60:
        return "很久"
    year, mon = divmod(t,  365 * 24 * 60 * 60)
    mon, day = divmod(mon,  30 * 24 * 60 * 60)
    day, hour = divmod(day,  24 * 60 * 60)
    hour, min = divmod(hour, 60 * 60)
    min, sec = divmod(min,  60)

    rtnstr = ''
    if year: rtnstr = str(year) + '年'
    elif mon: rtnstr = str(mon) + '月'
    elif day: rtnstr = str(day) + '天'
    elif hour: rtnstr = str(hour) + '小时'
    elif min: rtnstr = str(min) + '分钟'
    elif sec: rtnstr = str(sec) + '秒'

    return rtnstr


@app.template_filter('opeartionintervalcolor')
def opeartionintervalcolor(t):
    if t <= 5 * 60:
        return 'success'
    elif t <= 15 * 60:
        return 'info'
    elif t <= 60 * 60:
        return 'warning'
    else:
        return 'important'

'''
@app.template_filter('showqq')
def showqq(qq):
    if qq:
        rtnstr = "%s <a target='blank' href='http://wpa.qq.com/msgrd?V=1&Uin=%s'><img border='0' src='http://wpa.qq.com/pa?p=1:%s:10' /> </a>" % (qq,qq,qq)
    else:
        rtnstr = ''
    return rtnstr
'''
