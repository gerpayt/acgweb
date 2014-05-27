# coding: utf-8
from flask import render_template, request, redirect, url_for, json, flash, session, jsonify, abort
from acgweb import app, db
from sqlalchemy import or_
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from acgweb.model.schedule import Schedule
from acgweb.model.member import Member
from acgweb.form.activity import ActivityForm
import acgweb.const as CONST
from acgweb import config
from template_filter import *
from decorated_function import *
from acgweb.controller import mail
import time


@app.route('/activitylist-p<int:pagenum>')
@app.route('/activitylist')
@login_required
def activitylist(pagenum=1):
    """Page: all activitylist"""
    activity_count = Activity.query.filter(Activity.start_time > int(time.time()), Activity.status != 0).count()
    activity_list = Activity.query.filter(Activity.start_time > int(time.time()), Activity.status != 0)\
        .order_by('start_time ASC').limit(CONST.activity_per_page).offset(CONST.activity_per_page*(pagenum-1))
    return render_template('activity/activitylist.html',
        activity_list=activity_list,
        page_count=(activity_count-1)/CONST.activity_per_page+1,page_current=pagenum)


@app.route('/activitymanage-p<int:pagenum>')
@app.route('/activitymanage')
@login_required
def activitymanage(pagenum=1):
    """Page: all activitylist"""
    if not session.get('is_arra_monitor'):
        abort(403)
    activity_count = Activity.query.filter(Activity.start_time > int(time.time())-3*86400).count()
    activity_list = Activity.query.filter(Activity.start_time > int(time.time())-3*86400).order_by('start_time ASC')\
        .limit(CONST.activity_per_page).offset(CONST.activity_per_page*(pagenum-1))
    return render_template('activity/activitymanage.html',
        activity_list=activity_list,
        page_count=(activity_count-1)/CONST.activity_per_page+1,page_current=pagenum)


@app.route('/activity-<int:activity_id>')
@login_required
def activitydetail(activity_id):
    """Page: activity detail"""
    if request.method == 'GET':
        activity = Activity.query.get_or_404(activity_id)
        is_busy = Duty.query.filter(Duty.uid==session['uid'], Duty.aid==activity_id).count()
        duty = Duty.query.filter(Duty.uid==session['uid'], Duty.aid==activity_id).first()
        if duty:
            is_success = duty.status==10
        else:
            is_success = False
        return render_template('activity/activitydetail.html', activity=activity, is_busy=is_busy, is_success=is_success)
    else:
        activity = Activity.query.get(activity_id)
        if activity.status == 2 or activity.status == 3:
            duty = Duty.query.filter(Duty.aid==activity_id, Duty.uid==session['uid']).first()
            
            type = request.form['type']
            content = request.form['content']
            duty.appendlog(type, content)
            db.session.add(activity)
            db.session.commit()
            # 根据不同的类型来通知不同的人 #TODO
            return jsonify(result='ok',msg='成功')
        else:
            return jsonify(result='err',msg='非法操作，请重试。')

@app.route('/activityopeartion-<opeartion>-<int:duty_id>', methods=['GET', 'POST'])
@login_required
def activityopeartion(opeartion,duty_id):
    """Page: activity detail"""
    duty = Duty.query.get_or_404(duty_id)
    if duty.activity.status == 1 and ( not Duty.query.filter(Duty.id != duty_id,Duty.uid==session['uid'], Duty.aid==duty.aid).count() ) and \
        ((session['uid'] == duty.member.uid and opeartion in CONST.duty_status_opeartion_selfuser_mapper[duty.status]) or \
        (session['uid'] != duty.member.uid and opeartion in CONST.duty_status_opeartion_otheruser_mapper[duty.status]) or \
        (session.get('is_arra_monitor') and opeartion in CONST.duty_status_opeartion_monitor_mapper[duty.status])):
        #print Article.query.filter(Article.title==article_title).statement
        if request.method=='POST':
            content = request.form['content']
        else:
            content = ''
        if CONST.dutyoperationname[opeartion].has_key('require_input') and not content:
            flash({'type':'error', 'content':'请填写申请理由。'})
            return redirect(url_for('activitydetail',activity_id=duty.aid))

        if opeartion == 'cover_duty':
            if Duty.query.filter(Duty.uid==session['uid'], Duty.aid==duty.aid).count():
                flash({'type':'danger', 'content':'你在本时间段已经有此活动，请勿重复选班。'})
                return redirect(url_for('activitydetail',activity_id=duty.aid))
            else:
                timestr = timeformat_filter(duty.activity.start_time,"%Y-%m-%d %H:%M")
                venue = venuename_filter(duty.activity.venue)
                title = duty.activity.title
                remark = duty.activity.remark
                url = config.BASE_URL + url_for('activitydetail',activity_id=duty.activity.id)
                member_url = config.BASE_URL + url_for('memberdetail',member_uid=session['uid'])
                member_name = session['name']
                subject = mail.cover_duty_tmpl['subject']
                content = mail.cover_duty_tmpl['content'] % ( member_url, member_name, timestr, venue, title, remark, url , url )
                mail.send_message(duty.uid,session['uid'],subject,content,2)
                mail.send_mail(subject, content, duty.uid, duty.member.email)

                new_duty = Duty(aid=duty.aid,uid=session['uid'],status=6,log='')
                new_duty.appendprocesse('cover_task','')
                db.session.add(new_duty)
        elif opeartion == 'approve_apply' or opeartion == 'decline_apply':
            timestr = timeformat_filter(duty.activity.start_time,"%Y-%m-%d %H:%M")
            venue = venuename_filter(duty.activity.venue)
            title = duty.activity.title
            remark = duty.activity.remark
            url = config.BASE_URL + url_for('activitydetail',activity_id=duty.activity.id)
            if opeartion == 'approve_apply':
                subject = mail.approve_apply_tmpl['subject']
                content = mail.approve_apply_tmpl['content'] % ( timestr, venue, title, remark, url , url )
            else:
                subject = mail.decline_apply_tmpl['subject']
                content = mail.decline_apply_tmpl['content'] % ( timestr, venue, title, remark, url , url )
            mail.send_message(duty.uid,session['uid'],subject,content,2)
            mail.send_mail(subject, content, duty.uid, duty.member.email)

        duty.status = CONST.duty_status_opeartion_next[opeartion]
        duty.appendprocesse(opeartion,content)
        db.session.add(duty)
        db.session.commit()
        flash({'type':'success', 'content':'操作成功！'})
    else:
        flash({'type':'danger', 'content':'非法操作，请重试。'})
    return redirect(url_for('activitydetail',activity_id=duty.aid))

@app.route('/activityapply-<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activityapply(activity_id):
    """Page: activity detail"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == 1 and (not Duty.query.filter(Duty.uid==session['uid'], Duty.aid==activity_id).count() ):
        content = request.form['content']
        if not content:
            flash({'type':'error', 'content':'请填写申请理由。'})
        else:
            newduty = Duty(aid=activity_id,uid=session['uid'],status=1,process='',log='')
            newduty.appendprocesse('apply_duty',content)
            db.session.add(newduty)
            db.session.commit()
            flash({'type':'success', 'content':'值班申请提交成功，等待排版班长审核。'})
    else:
        flash({'type':'danger', 'content':'非法操作，请重试。'})
    return redirect(url_for('activitydetail',activity_id=activity_id))


@app.route('/activityedit-<int:activity_id>', methods=['GET', 'POST'])
@login_required
def activityedit(activity_id):
    """Page: activity detail"""

    if request.method == 'POST':
        form = ActivityForm(request.form)
        if form.validate_on_submit():
            if not form.errors:
                pass#form.username.errors.append('帐号已存在')
        #print form.errors
        if not form.errors:
            activity = Activity.query.get(form.id.data)
            if not session.get('is_arra_monitor'):
                abort(403)
            if not activity: activity = Activity()
            info_modify = str(activity.title)!=str(form.title.data) or str(activity.venue)!=str(form.venue.data) or str(activity.start_time)!=str(form.start_time.data)
            if info_modify:
                dutylist = Duty.query.filter(Duty.aid==activity_id).all()

                timestr = timeformat_filter(activity.start_time,"%Y-%m-%d %H:%M")
                timestr_new = timeformat_filter(form.start_time.data,"%Y-%m-%d %H:%M")
                venue = venuename_filter(activity.venue)
                venue_new = venuename_filter(form.venue.data)
                title = activity.title
                title_new = form.title.data
                remark = activity.remark
                url = config.BASE_URL + url_for('activitydetail',activity_id=activity.id)
                subject = mail.activity_modify_tmpl['subject']
                content = mail.activity_modify_tmpl['content'] % ( timestr, timestr_new, venue, venue_new, title, title_new, remark, url , url )
                for duty in dutylist:
                    mail.send_message(duty.uid,session['uid'],subject,content,2)
                    mail.send_mail(subject, content, duty.uid, duty.member.email)

            activity.title=form.title.data
            activity.remark=form.remark.data
            activity.venue=form.venue.data
            activity.start_time=form.start_time.data
            activity.end_time=form.end_time.data
            activity.type=form.type.data
            activity.status=form.status.data
            activity.hostname=form.hostname.data
            db.session.add(activity)
            db.session.commit()

            flash({'type':'success', 'content':'保存成功！'})
            return redirect('/activitymanage')
        return render_template('activity/activityedit.html', form=form)

    else:
        activity = Activity.query.get_or_404(activity_id)
        if not session.get('is_arra_monitor'):
            abort(403)
        form = ActivityForm(obj=activity)
        if Duty.query.filter(Duty.aid==activity_id).count():
            flash({'type':'warning', 'content':'已有音控员负责此活动，请谨慎操作！'})
        return render_template('activity/activityedit.html', form=form)



@app.route('/activityarrange-<int:activity_id>')
@login_required
def activityarrange(activity_id):
    """Page: activity detail"""
    activity = Activity.query.get_or_404(activity_id)
    available_member = {}
    if activity.status == 1 and session.get('is_arra_monitor'):
        schedulelist = Schedule.query.all()
        memberlist = Member.query.filter(or_(Member.type==1, Member.type==3)).all()
        busymember={}
        for s in schedulelist:
            if busymember.has_key(s.uid):
                continue
            s.strtolist()
            st = activity.getstrustarttime()
            print st['week'], s.weeklist, st['weekday'], s.weekdaylist
            if st['week'] in s.weeklist and st['weekday'] in s.weekdaylist:
                if st['start_section'] in s.sectionlist or st['start_section']+3 in s.sectionlist:
                    busymember[s.uid] = s.classtype
        print busymember
        hour = time.localtime(activity.start_time).tm_hour
        print activity.start_time,hour
        starttime = activity.start_time - 1 * 3600
        endtime = activity.start_time + 2 * 3600
        activitylist = Activity.query.filter(Activity.start_time >= starttime, Activity.start_time <= endtime).all()
        for a in activitylist:
            for d in a.duties:
                busymember[d.uid] = 9
        for member in memberlist:
            m = {'uid':member.uid, 'name':member.name, 'mobile_num':member.mobile_num, 'qqnum':member.qqnum, 'email':member.email,
                 'available':busymember.get(member.uid,0), 'venue':0, 'start_time':0, 'weekcount':0, 'monthcount':0}
            available_member[member.uid]=m


        # get last duty time and venue
        sql = "select a.uid, b.venue, max(b.start_time) as start_time from duty as a left join activity as b on a.aid = b.id where a.status=11 group by a.uid"
        res = db.session.execute(sql)
        for r in res:
            (uid,venue,start_time) = r
            if uid in available_member.keys():
                available_member[uid]['venue'] = venue
                available_member[uid]['start_time'] = start_time


        # get lst week and last month count
        sql = "select a.uid, count(1) as count from duty as a left join activity as b on a.aid = b.id where a.status=11 and b.start_time> %d and b.start_time< %d group by a.uid"
        now = int(time.time())
        last_week = now - 7 * 86400
        last_month = now - 30 * 86400
        res = db.session.execute(sql%(now, last_week))
        for r in res:
            (uid,weekcount) = r
            if uid in available_member.keys():
                available_member[uid]['weekcount'] = weekcount
        res = db.session.execute(sql%(now, last_month))
        for r in res:
            (uid,monthcount) = r
            if uid in available_member.keys():
                available_member[uid]['monthcount'] = monthcount

    else:
        flash({'type':'danger', 'content':'非法操作，请重试。'})
    print available_member.values()
    return render_template('activity/activityarrange.html', activity=activity, available_member=available_member.values())





@app.route('/activityappoint-<int:activity_id>-<member_uid>')
@login_required
def activityappoint(activity_id,member_uid):
    """Page: activity detail"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == 1 and session.get('is_arra_monitor'):
        member = Member.query.get(member_uid)
        if not Duty.query.filter(Duty.aid==activity_id, Duty.uid==member_uid).count():
            duty = Duty()
            duty.aid = activity_id
            duty.uid = member_uid
            duty.status = 4
            duty.log = ''
            duty.appendprocesse('activity_appoint','排班班长安排值班')
            db.session.add(duty)
            db.session.commit()
            # need or not
            timestr = timeformat_filter(activity.start_time,"%Y-%m-%d %H:%M")
            venue = venuename_filter(activity.venue)
            title = activity.title
            remark = activity.remark
            url = config.BASE_URL + url_for('activitydetail',activity_id=activity.id)
            subject = mail.activity_appoint_tmpl['subject']
            content = mail.activity_appoint_tmpl['content'] % ( timestr, venue, title, remark, url , url )
            mail.send_message(member_uid,session['uid'],subject,content,2)
            mail.send_mail(subject, content, member_uid, member.email)

        else:
            flash({'type':'danger', 'content':'此人已经安排过值班任务。'})
    else:
        flash({'type':'danger', 'content':'非法操作，请重试。'})
    return redirect(url_for('activitydetail',activity_id=activity_id))



@app.route('/activityready-<int:activity_id>')
@login_required
def activityready(activity_id):
    """Page: activity detail"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == 0 and session.get('is_arra_monitor'):
        #print Article.query.filter(Article.title==article_title).statement
        flash({'type':'success', 'content':'活动已经就绪。'})
        activity = Activity.query.get_or_404(activity_id)
        activity.status = 1
        db.session.add(activity)
        db.session.commit()
    else:
        flash({'type':'danger', 'content':'非法操作，请重试。'})
    return redirect(url_for('activitydetail',activity_id=activity_id))



@app.route('/activitycancle-<int:activity_id>')
@login_required
def activitycancle(activity_id):
    """Page: activity detail"""
    activity = Activity.query.get_or_404(activity_id)
    if (activity.status == 1 or activity.status == 0) and session.get('is_arra_monitor'):
        #print Article.query.filter(Article.title==article_title).statement
        flash({'type':'success', 'content':'活动已经取消。'})
        activity = Activity.query.get_or_404(activity_id)
        activity.status = 4
        duties = Duty.query.filter(Duty.aid==activity_id)

        timestr = timeformat_filter(activity.start_time,"%Y-%m-%d %H:%M")
        venue = venuename_filter(activity.venue)
        title = activity.title
        remark = activity.remark
        url = config.BASE_URL + url_for('activitydetail',activity_id=activity.id)
        subject = mail.activity_cancle_tmpl['subject']
        content = mail.activity_cancle_tmpl['content'] % ( timestr, venue, title, remark, url , url )

        for duty in duties:
            # 通知音控员取消了活动 #TODO

            mail.send_message(duty.uid,session['uid'],subject,content,2)
            mail.send_mail(subject, content, duty.uid, duty.member.email)

            duty.status=9
            db.session.add(duty)
        db.session.add(activity)
        db.session.commit()
    else:
        flash({'type':'danger', 'content':'非法操作，请重试。'})
    return redirect(url_for('activitydetail',activity_id=activity_id))


@app.route('/activityterminate-<int:activity_id>', methods=['GET','POST'])
@login_required
def activityterminate(activity_id):
    """Page: activity detail"""
    activity = Activity.query.get_or_404(activity_id)
    if activity.status == 2 and Duty.query.filter(Duty.uid==session['uid'], Duty.aid==activity_id).count():
        #print Article.query.filter(Article.title==article_title).statement
        last_time = int(request.form['end_time']) - activity.start_time
        if last_time < 30 * 60 or last_time > 6 * 3600:
            flash({'type':'danger', 'content':'活动结束时间填写有误。'})
        else:
            activity.end_time = int(request.form['end_time'])
            activity.status = 3
            duties = Duty.query.filter(Duty.aid==activity_id)
            for duty in duties:
                duty.status=11
                db.session.add(duty)
            db.session.add(activity)
            db.session.commit()
            flash({'type':'success', 'content':'活动已经成功标记为结束状态。'})
    else:
        flash({'type':'danger', 'content':'非法操作，请重试。'})
    return redirect(url_for('activitydetail',activity_id=activity_id))


@app.route('/activityjson')
@login_required
def activityjson():
    activity = Activity.query.all()
    activity_list = []
    for a in activity:
        d={'id':a.id, 'venue':a.venue, 'start_time':a.start_time, 'end_time':a.end_time, 'type':a.type, 'title':a.title, 'remark':a.remark}
        activity_list.append(d)
    rtn = json.dumps(activity_list)
    return rtn


@app.route('/activitysync')
@login_required
def activitysync():
    from acgweb.controller.spider import activity_spider
    log = activity_spider()
    return '<br /> \n'.join(log)


# cron every half hour
@app.route('/cron')
def cron():
    try:
        last_cron = int(open(config.BASE_DIR+'data/last_cron.time','r').read())
    except:
        last_cron = 0
    now = int(time.time())
    if last_cron / (30*60) < now / (30*60):
        now =  now / (30*60) * (30*60)
        log = []
        # 2 hours before activity start
        activitylist = Activity.query.filter(Activity.start_time>= now+7150, Activity.start_time<now+8950, Activity.status==1).all()
        for activity in activitylist:
            timestr = timeformat_filter(activity.start_time,"%Y-%m-%d %H:%M")
            venue = venuename_filter(activity.venue)
            title = activity.title
            remark = activity.remark
            url = config.BASE_URL + url_for('activitydetail',activity_id=activity.id)
            subject = mail.activity_nearly_begin_tmpl['subject']
            content = mail.activity_nearly_begin_tmpl['content'] % ( timestr, venue, title, remark, url , url )
            for duty in activity.duties:
                mail.send_mail(subject, content, duty.uid, duty.member.email)
                #log.append("notice "+)

        # on activity start
        activitylist = Activity.query.filter(Activity.start_time>= now-50 , Activity.start_time<now+1750, Activity.status==1).all()
        for activity in activitylist:
            activity.status = 2
            db.session.add(activity)
        dutylist = Duty.query.join(Activity).filter(Activity.start_time>= now-50 , Activity.start_time<now+1750, Activity.status==1, or_(Duty.status==6,Duty.status==7)).all()
        # TODO other duty status
        for duty in dutylist:
            duty.status = 10
            db.session.add(duty)
        db.session.commit()

        # 6 hours after activity start

        open(config.BASE_DIR+'data/last_cron.time','w').write(str(now))

        return "now"+str(now)
    else:
        return "last_cron"+str(last_cron)

