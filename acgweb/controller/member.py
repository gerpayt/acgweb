# coding: utf-8
from flask import render_template, request, redirect, url_for, json, flash, abort, session
from acgweb import app, db
from acgweb.model.member import Member
import template_filter
from acgweb.form.member import MemberForm
from decorated_function import *
import acgweb.const as CONST
from acgweb import config
import md5,time

@app.route('/memberlist-p<int:pagenum>')
@app.route('/memberlist')
@login_required
def memberlist(pagenum=1):
    """Page: all activitylist"""
    member_count = Member.query.count()
    member_list = Member.query.order_by('uid DESC').limit(CONST.member_per_page).offset(CONST.member_per_page*(pagenum-1))
    return render_template('member/memberlist.html',
        member_list=member_list,
        page_count=(member_count-1)/CONST.member_per_page+1,page_current=pagenum)

@app.route('/member-<member_uid>')
@login_required
def memberdetail(member_uid):
    """Page: activity detail"""
    member = Member.query.get_or_404(member_uid)
    schedule_table = {}
    weeknum = int((time.time())-config.SEMASTER_BASE )/ (7*86400) + 1
    weekstart = int(time.time())-86400 * (time.localtime().tm_wday+1)
    startstr = time.strftime("%Y-%m-%d", time.localtime(weekstart))
    endstr = time.strftime("%Y-%m-%d", time.localtime(weekstart+7*86400))

    try:
        fp = open(config.BASE_DIR+'cache/st_%s.log' % member_uid,'r')
    except:
        pass#schedule_table = {}
        fp = open(config.BASE_DIR+'cache/st_empty.log','r')

    for line in fp:
        timestr = line[:10]
        if timestr >= startstr and timestr < endstr:
            line = line.rstrip('\n')
            schedule_content = line[11:].split('\t')
            schedule_table[timestr] = schedule_content
    print schedule_table
    return render_template('member/memberdetail.html', member=member, schedule_table=schedule_table, weekstart=weekstart, weeknum=weeknum)


@app.route('/membermanage-p<int:pagenum>')
@app.route('/membermanage')
@login_required
def membermanage(pagenum=1):
    """Page: all activitylist"""
    if not session.get('is_arra_monitor'):
        abort(403)
    member_count = Member.query.count()
    member_list = Member.query.order_by('uid DESC').limit(CONST.member_per_page).offset(CONST.member_per_page*(pagenum-1))
    return render_template('member/membermanage.html',
        member_list=member_list,
        page_count=(member_count-1)/CONST.member_per_page+1,page_current=pagenum)


@app.route('/memberedit', methods=['GET', 'POST'])
@app.route('/memberedit-<member_uid>', methods=['GET', 'POST'])
@login_required
def memberedit(member_uid=''):

    if request.method == 'POST':
        form = MemberForm(request.form)
        if form.validate_on_submit():
            if not member_uid and Member.query.filter(Member.uid==form.uid.data).count():
                form.uid.errors.append('学号已存在')
            if Member.query.filter(Member.email==form.email.data, Member.uid != member_uid).count():
                form.email.errors.append('电子邮箱已存在')
            if Member.query.filter(Member.mobile_num==form.mobile_num.data, Member.uid != member_uid).count():
                form.mobile_num.errors.append('手机号码已存在')

        if not form.errors:
            member = Member.query.get(member_uid)
            if not session.get('is_arra_monitor'):
                abort(403)
            if not member:
                member = Member()
                member.uid=form.uid.data
                key = md5.new()
                key.update(form.mobile_num.data)
                member.password=key.hexdigest()
                member.update_register_time()
                member.update_lastlogin_time()
            else:
                member.uid=member_uid
            member.name=form.name.data
            member.sex=form.sex.data
            member.school=form.school.data
            member.mobile_num=form.mobile_num.data
            member.mobile_type=form.mobile_type.data
            member.mobile_short=form.mobile_short.data
            member.qqnum=form.qqnum.data
            member.email=form.email.data
            member.address=form.address.data
            member.credit_card=form.credit_card.data
            member.type=form.type.data
            member.introduce=form.introduce.data
            db.session.add(member)
            db.session.commit()

            flash({'type':'success', 'content':'保存成功！'})
            return redirect('/membermanage')
        return render_template('member/memberedit.html', form=form, member_uid=member_uid)
    else:
        member = Member.query.get(member_uid)
        if not session.get('is_arra_monitor'):
            abort(403)
        form = MemberForm(obj=member)

        return render_template('member/memberedit.html', form=form, member_uid=member_uid)



@app.route('/memberdelete-<member_uid>')
@login_required
def memberdelete(member_uid):
    """Page: activity detail"""
    if not session.get('is_arra_monitor'):
        abort(403)
    member = Member.query.get(member_uid)
    db.session.delete(member)
    db.session.commit()
    # TODO delete relation
    # schedule cache duty message
    flash({'type':'success', 'content':'成员已删除。'})
    return redirect(url_for('membermanage'))



@app.route('/memberjson')
@login_required
def memberjson():
    member = Member.query.all()
    member_list = []
    for a in member:
        d={'uid':a.uid, 'name':a.name, 'school':a.school}
        member_list.append(d)
    rtn = json.dumps(member_list)
    return rtn

