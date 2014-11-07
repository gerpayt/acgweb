# coding: utf-8
import time

from flask import render_template, json, abort, flash, make_response
from acgweb import app, db
from acgweb.model.activity import Activity
from acgweb.model.member import Member
from acgweb.form.schedule import ScheduleForm
import acgweb.const as CONST
from acgweb import config
from decorated_function import *


@app.route('/partner')
@login_required
def partner():
    support1 = 1
    support2 = 3

    from_time = 0
    sql = "select count(1) as cnt, group_concat(d.uid) as uids, a.*, d.* FROM activity as a left join duty as d on d.aid = a.id where a.start_time >= %d and d.status in (%s) group by a.id order by d.uid asc"\
          % (from_time, ','.join([str(CONST.DUTY_ACTIVITY_ENDED), str(CONST.DUTY_ACTIVITY_ONGOING)]))

    data = list(db.session.execute(sql))

    fp1 = {}
    # scan candidate in fp1
    for activity in data:
        uids = activity.uids.split(',')
        for uid in uids:
            if uid not in fp1:
                fp1[uid] = 0
            fp1[uid] += 1

    # delete candidate below support1
    for item in fp1.keys():
        if fp1[item] < support1:
            del fp1[item]

    fp2 = {}
    # generate candidate in fp2
    uids1 = fp1.keys()
    uids1.sort()

    #for i in uids1:
    #    print i

    i = 0
    for item1 in uids1:
        i += 1
        for item2 in uids1[i:]:
            key = (item1, item2)
            fp2[key] = 0

    uids2 = fp2.keys()
    uids2.sort()

    #for i in uids2:
    #    print i

    # scan candidate in fp2
    for activity in data:
        uids = activity.uids.split(',')
        if len(uids) < 2:
            continue
        i = 0

        # generate 2-item subsets of a activity
        for item1 in uids:
            i += 1
            for item2 in uids[i:]:
                key = (item1, item2)
                if key in fp2:
                    fp2[key] += 1

    # delete candidate below support2
    for item in fp2.keys():
        if fp2[item] < support2:
            del fp2[item]

    tmp = sorted(fp2.items(), key=lambda e: e[1], reverse=True)

    partner_list = []
    for item in tmp:
        member_list = []
        uids = item[0]
        for uid in uids:
            member = Member.query.get_or_404(uid)
            member_list.append(member)

        partner_list.append({'members': member_list, 'count': item[1]})

    return render_template('other/partner.html', partner_list=partner_list)
