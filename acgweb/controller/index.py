# coding: utf-8
from flask import render_template
from acgweb import app, db
from acgweb.model.activity import Activity
from acgweb.model.article import Article
from acgweb.model.duty import Duty
#from sqlalchemy import func, desc
import acgweb.const as CONST
from decorated_function import *
import time


@app.route('/index')
@app.route('/')
@login_required
def siteindex():
    """Site index method"""
    now = int(time.time())
    article_notice = Article.query.filter(Article.cate_id == 1).order_by(Article.posttime.desc()).first()
    activity_list = Activity.query.filter(Activity.start_time > now, Activity.status != CONST.ACTIVITY_UNKNOWN, Activity.status != CONST.ACTIVITY_CANCELED).order_by(Activity.start_time).limit(CONST.activity_index_num)
    article_list = Article.query.order_by(Article.posttime.desc()).limit(CONST.article_index_num)
    duty_list = Duty.query.join(Activity).filter(Duty.uid == session[u'uid'], Activity.start_time > now).order_by(Activity.start_time).limit(CONST.duty_index_page)
    #rank_list = Duty.query.group_by(Duty.uid).order_by('sumtime ASC').limit(CONST.rank_index_page)
    ### 3qto kongkongyzt  #db.session.query(Activity).order_by(desc('end_time-start_time')).all()
    struct_now = time.localtime()
    month_start = int(time.mktime((struct_now.tm_year, struct_now.tm_mon, 1, 0, 0, 0, 0, 0, 0)))

    sql = "select c.uid, c.name, sum(b.end_time-b.work_start_time) as totaltime from duty as a left join activity as b on a.aid = b.id left join member as c on c.uid = a.uid where b.end_time != '0' and b.start_time > '%d' and b.end_time < %d and a.status = '11' group by a.uid order by totaltime desc limit %s " % (month_start, int(time.time()), CONST.rank_index_page)
    #if config.DEBUG: print sql
    # BUG?
    res = db.session.execute(sql)
    rank_list = []
    for i, r in enumerate(res):
        d = {'uid': r[0], 'rank': i + 1, 'name': r[1], 'time': r[2]}
        rank_list.append(d)
    #if config.DEBUG: print rank_list
    if viewtype() == 1:
        return render_template('site/index_mobile.html',
            article_notice=article_notice, activity_list=activity_list, article_list=article_list, duty_list=duty_list, rank_list=rank_list)
    else:
        return render_template('site/index.html',
            article_notice=article_notice, activity_list=activity_list, article_list=article_list, duty_list=duty_list, rank_list=rank_list)
