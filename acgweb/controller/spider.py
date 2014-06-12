# -- coding:utf-8 --
from flask import url_for
from acgweb import db
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from template_filter import *
from acgweb import config
from acgweb.controller import mail
import urllib2, json, MySQLdb
#from acttypeclassify import acttype
import time


def activity_spider():
    log = []
    url = 'http://vrs.husteye.cn/Api'
    sid2ven = {u'5':1,u'8':2,u'10':3}
    #Fetch contents
    try:
        if config.HTTP_PROXY:
            proxy_handler = urllib2.ProxyHandler({"http" : config.HTTP_PROXY})  
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
        content = urllib2.urlopen(url).read()
    except:
        log.append('Can\'t fetch vrs api' )
        content = ''
    #print content
    #Parse contents

    activities = json.loads(content)
    for act in activities:
        oid = act['id']
        title = act['activity']
        remark = act['remark']
        venue = sid2ven[act['sid']]
        start_time = act['time']
        #type = acttype(title)
        type = 0
        #if exist

        sql = 'select id,venue,title,remark,start_time from activity where oid = "%s";' % oid
        #print 'test oid:'+oid
        res = db.session.execute(sql)
        db.session.commit()
        if not res.rowcount:
            sql = 'insert into activity ( oid, title, remark, venue, start_time, type, status) values ("%s", "%s", "%s", "%s", "%s", "%s", "1");' % (oid, title, remark, venue, start_time, type)
            #print sql
            # help! Done
            new_obj = db.session.execute(sql)
            #print new_obj.lastrowid
            db.session.commit()
            new_id = new_obj.lastrowid
            log.append('New record inserted new_id:%s oid=%s.' % (new_id, oid) )
        else:
            d={}
            for r in res:
                d = {'id':r[0], 'sid':r[1], 'title':r[2], 'remark':r[3], 'time':r[4] }
            #print d
            #print str(title) , str(d['title']) , remark , d['remark'], venue , d['sid'] , start_time , d['time']
            if str(title)[:32] != str(d['title'])[:32] or str(remark) != str(d['remark']) or str(venue) != str(d['sid']) or str(start_time) != str(d['time']):
                sql = 'update activity set title = "%s", remark = "%s", venue = "%s", start_time = "%s" where oid = "%s";' % (title, remark, venue, start_time, oid)
                db.session.execute(sql)
                db.session.commit()
                log.append('Same record exists but modified id: %s oid:%s.' % (d['id'], oid) )

                duty_list = Duty.query.filter(Duty.aid==d['id']).all()

                timestr_old = timeformat_filter(d['time'],"%Y-%m-%d %H:%M")
                timestr_new = timeformat_filter(start_time,"%Y-%m-%d %H:%M")
                venue_old = venuename_filter(d['sid'])
                venue_new = venuename_filter(venue)
                title_old = d['title']
                title_new = title
                activity = Activity.query.get(d['id'])
                url = config.BASE_URL + url_for('activitydetail',activity_id=activity.id)
                subject = mail.activity_modify_tmpl['subject']
                content = mail.activity_modify_tmpl['content'] % ( timestr_old, timestr_new, venue_old, venue_new, title_old, title_new, remark, url , url )
                for duty in duty_list:
                    mail.send_message(duty.uid,'ADMIN',subject,content,2)
                    mail.send_mail(subject, content, duty.uid, duty.member.email)
            else:
                pass#log.append('Same record exists ignore' )
            #print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
    db.session.commit()
    log.append('Success on %s.' % time.strftime('%Y-%m-%d %H:%M:%S') )

    return log
