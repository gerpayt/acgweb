# coding: utf-8
from flask import render_template, send_file
from acgweb import app, db
from acgweb.model.activity import Activity
from acgweb.model.article import Article
from acgweb.model.member import Member
from acgweb.model.message import Message
from acgweb.model.duty import Duty
import acgweb.const as CONST
from acgweb import config
from decorated_function import *
from acgweb.controller.mail import get_out_box
import os
import sms


@app.route('/manage')
@login_required
def manage():
    """Page: all activitylist"""
    count = {}
    count['activity'] = Activity.query.count()
    count['member'] = Member.query.count()
    count['duty'] = Duty.query.count()
    count['article'] = Article.query.count()
    count['message'] = Message.query.count()

    count['send_sms'], count['rest_sms'] = sms.query_sms()

    param = {}
    try:
        param['last_sync'] = int(open(config.BASE_DIR + 'data/last_sync.time', 'r').read())
    except:
        param['last_sync'] = 0
    try:
        param['last_cron'] = int(open(config.BASE_DIR + 'data/last_cron.time', 'r').read())
    except:
        param['last_cron'] = 0
    #if config.DEBUG: print config.BASE_DIR+'data/last_cron.time'
    return render_template('manage/manage.html', count=count, param=param)


@app.route('/salarymanage')
@login_required
def salarymanage():
    """Page: all activitylist  and a.status = '11' """
    starttime = request.args.get('starttime', config.SEMESTER_BASE)
    if not starttime: starttime = 0
    endtime = request.args.get('endtime', CONST.max_time)
    if not endtime: endtime = CONST.max_time
    export = request.args.get('export', None)

    sql1 = "select c.uid, b.id, b.work_start_time, b.start_time, b.end_time, b.venue, b.title, b.end_time-b.work_start_time as work_last_time from duty as a left join activity as b on a.aid = b.id left join member as c on c.uid = a.uid where b.end_time != '0' and b.start_time > '%d' and b.end_time < %d and a.status = '11' order by b.start_time " % (int(starttime), int(endtime))
    #print sql1
    res1 = db.session.execute(sql1)
    salalist = {}
    for i in res1:
        if not salalist.has_key(i.uid):
            salalist[i.uid] = []
        salalist[i.uid].append({'aid': i.id, 'work_start_time': i.work_start_time, 'end_time': i.end_time, 'venue': i.venue, 'title': i.title, 'work_last_time': i.work_last_time})
    #print salalist
    sql2 = "select c.uid, c.name, c.credit_card, sum(b.end_time-b.work_start_time) as totaltime from duty as a left join activity as b on a.aid = b.id left join member as c on c.uid = a.uid where b.end_time != '0' and b.start_time > '%d' and b.end_time < %d and a.status = '11' group by a.uid order by convert(c.name using gb2312) ASC " % (int(starttime), int(endtime))
    #print sql2
    res2 = db.session.execute(sql2)
    #print res2
    rank_list = []
    for i, r in enumerate(res2):
        d = {'uid': r[0], 'rank': i + 1, 'name': r[1], 'time': r[3], 'salalist': salalist[r[0]], 'credit_card': r[2]}
        rank_list.append(d)
    #print rank_list
    if starttime == 0: starttime = ''
    if endtime == CONST.max_time: endtime = ''
    if export:
        from acgweb.controller.export import export_salary
        wb = export_salary(rank_list, starttime, endtime)
        tmp_filename = config.BASE_DIR + 'temp/salary.xls'
        wb.save(tmp_filename)
        #if config.DEBUG: print tmp_filename
        response = send_file(tmp_filename, as_attachment=True, attachment_filename='salary.xls')
        os.unlink(tmp_filename)
        return response
    else:
        return render_template('manage/managesalary.html', rank_list=rank_list, salaperhour=CONST.salaperhour, starttime=starttime, endtime=endtime)


@app.route('/venuemanage')
@login_required
def venuemanage():
    """Page: all activitylist"""
    return render_template('manage/managevenue.html')


@app.route('/mailmanage')
@login_required
def mailmanage():
    mail_list = get_out_box()
    return render_template('manage/managemail.html', mail_list=mail_list)
#邮件


@app.route('/logmanage')
@login_required
def logmanage():
    """Page: all activitylist"""
    logdict = {}
    for t in ['cron', 'sync', 'sms', 'push', 'error']:
        logs = []
        try:
            fp = open(config.BASE_DIR + 'log/%s.log' % t, 'r')
            logs = fp.readlines()[-100:]
            fp.close()
        except:
            pass
        logs.reverse()
        logdict[t] = logs

    return render_template('manage/managelog.html', cronlogs=logdict['cron'], synclogs=logdict['sync'], smslogs=logdict['sms'], pushlogs=logdict['push'], errorlogs=logdict['error'])


@app.route('/systemmanage')
@login_required
def systemmanage():
    """Page: all activitylist"""
    return render_template('manage/managesystem.html')
