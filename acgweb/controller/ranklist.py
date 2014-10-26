# coding: utf-8
import time

from flask import render_template, json, abort, flash, make_response
from acgweb import app, db
from acgweb.model.schedule import Schedule
from acgweb.model.member import Member
from acgweb.form.schedule import ScheduleForm
import acgweb.const as CONST
from acgweb import config
from decorated_function import *


@app.route('/ranklist')
@login_required
def ranklist():
    rank_list = {}
    struct_now = time.localtime()
    month_start = int(time.mktime((struct_now.tm_year, struct_now.tm_mon, 1, 0, 0, 0, 0, 0, 0)))
    week_start = int(time.mktime((struct_now.tm_year, struct_now.tm_mon, struct_now.tm_mday, 0, 0, 0, 0, 0, 0))) - 86400 * (1+struct_now.tm_wday)
    # print month_start, week_start
    period_list = [{'name': 'all', 'title': '总排行', 'time': 0},
                   {'name': 'semester', 'title': '学期排行', 'time': config.SEMESTER_BASE},
                   {'name': 'month', 'title': '月排行', 'time': month_start},
                   {'name': 'week', 'title': '周排行', 'time': week_start}]
    sqltpl = "select c.uid, c.name, sum(b.end_time-b.work_start_time) as totaltime from duty as a left join activity as b on a.aid = b.id left join member as c on c.uid = a.uid where b.end_time != '0' and b.start_time > '%d' and b.end_time < %d and a.status = '11' group by a.uid order by totaltime desc limit %s "
    for period in period_list:
        sql = sqltpl % (period['time'], int(time.time()), 15)
        res = db.session.execute(sql)
        ranks = []
        for i, r in enumerate(res):
            d = {'uid': r[0], 'rank': i + 1, 'name': r[1], 'time': r[2]}
            ranks.append(d)
        rank_list[period['name']] = ranks

    return render_template('other/ranklist.html', rank_list=rank_list, period_list=period_list)
