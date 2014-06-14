# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, flash, send_file
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

    param = {}
    try:
        param['last_sync'] = int(open(config.BASE_DIR+'data/last_sync.time','r').read())
    except:
        param['last_sync'] = 0
    try:
        param['last_cron'] = int(open(config.BASE_DIR+'data/last_cron.time','r').read())
    except:
        param['last_cron'] = 0
    #if config.DEBUG: print config.BASE_DIR+'data/last_cron.time'
    return render_template('manage/manage.html',count=count,param=param)

@app.route('/salarymanage')
@login_required
def salarymanage():
    """Page: all activitylist  and a.status = '11' """
    starttime=request.args.get('starttime',0)
    if not starttime: starttime = 0
    endtime=request.args.get('endtime',CONST.max_time)
    if not endtime: endtime = CONST.max_time
    export = request.args.get('export',None)

    sql1 = "select c.uid, b.id, b.start_time, b.end_time, b.venue, b.title, b.end_time-b.start_time as last_time from duty as a left join activity as b on a.aid = b.id left join member as c on c.uid = a.uid where b.end_time != '0' and b.start_time > '%d' and b.end_time < %d and a.status = '11' order by b.start_time " % (int(starttime), int(endtime))
    #print sql1
    res1 = db.session.execute(sql1)
    salalist = {}
    for i in res1:
        if not salalist.has_key(i.uid):
            salalist[i.uid] = []
        salalist[i.uid].append({'aid':i.id,'start_time':i.start_time-3600,'end_time':i.end_time,'venue':i.venue,'title':i.title,'work_last_time':i.last_time+3600})
    #print salalist
    sql2 = "select c.uid, c.name, c.credit_card, sum(b.end_time-b.start_time+3600) as totaltime from duty as a left join activity as b on a.aid = b.id left join member as c on c.uid = a.uid where b.end_time != '0' and b.start_time > '%d' and b.end_time < %d and a.status = '11' group by a.uid order by totaltime " % (int(starttime), int(endtime))
    #print sql2
    res2 = db.session.execute(sql2)
    #print res2
    rank_list = []
    for i,r in enumerate(res2):
        d = {'uid':r[0],'rank':i+1,'name':r[1],'time':r[3],'salalist':salalist[r[0]],'credit_card':r[2]}
        rank_list.append(d)
    #print rank_list
    if starttime == 0: starttime = ''
    if endtime == CONST.max_time: endtime = ''
    if export:
        from acgweb.controller.export import export_salary
        wb = export_salary(rank_list,starttime,endtime)
        tmp_filename = config.BASE_DIR+'temp/salary.xls'
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
    logs=[]
    try:
        fp = open(config.BASE_DIR+'log/sync.log','r')
        logs = fp.readlines()[-100:]
        fp.close()
    except:
        pass
    try:
        last_sync_time = int(open(config.BASE_DIR+'data/last_sync.time','r').read())
    except:
        last_sync_time = 0
    logs.reverse()
    return render_template('activity/activitysync.html', last_sync_time=last_sync_time, logs=logs)


@app.route('/systemmanage')
@login_required
def systemmanage():
    """Page: all activitylist"""
    return render_template('manage/managesystem.html')

