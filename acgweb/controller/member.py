# coding: utf-8
import md5
import time
import os

from flask import render_template, json, flash, abort, make_response, send_file
from acgweb import app, db
from acgweb.model.activity import Activity
from acgweb.model.duty import Duty
from acgweb.model.member import Member
from acgweb.form.member import MemberForm
from decorated_function import *
import acgweb.const as CONST
from acgweb import config


@app.route('/memberlist-p<int:pagenum>')
@app.route('/memberlist')
@login_required
def memberlist(pagenum=1):
    """Page: all activitylist"""
    member_count = Member.query.count()
    member_list = Member.query.order_by('convert(name using gb2312) ASC').limit(CONST.member_per_page).offset(CONST.member_per_page * (pagenum - 1))
    if viewtype() == 1:
        return render_template('member/memberlist_mobile.html',
        member_list=member_list,
        page_count=(member_count - 1) / CONST.member_per_page + 1, page_current=pagenum)
    else:
        return render_template('member/memberlist.html',
        member_list=member_list,
        page_count=(member_count - 1) / CONST.member_per_page + 1, page_current=pagenum)


@app.route('/api/memberlist')
#@login_required
def memberlistapi():
    member_list = Member.query.order_by('convert(name using gb2312) ASC').all()
    res = []
    for member in member_list:
        d = {}
        d['uid'] = member.uid
        d['name'] = member.name
        d['mobile'] = member.mobile_num
        d['mobile_type'] = member.mobile_type
        d['mobile_short'] = member.mobile_short
        res.append(d)
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/memberdetail-<member_uid>')
#@login_required
def memberdetailapi(member_uid):
    member = Member.query.get(member_uid)
    res = {}
    res['uid'] = member.uid
    res['name'] = member.name
    res['type'] = member.type
    res['sex'] = member.sex
    res['school'] = member.school
    res['mobile'] = member.mobile_num
    res['mobile_type'] = member.mobile_type
    res['mobile_short'] = member.mobile_short
    res['email'] = member.email
    res['qqnum'] = member.qqnum
    res['address'] = member.address
    res['introduce'] = member.introduce
    res['photo'] = member.photo
    res['register_time'] = member.register_time
    res['lastlogin_time'] = member.lastlogin_time

    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/member-<member_uid>')
@login_required
def memberdetail(member_uid):
    """Page: activity detail"""
    member = Member.query.get_or_404(member_uid)
    schedule_table = {}
    weeknum = int((time.time()) - config.SEMESTER_BASE) / (7 * 86400) + 1
    if weeknum < 1:
        weeknum = 1
    elif weeknum > 25:
        weeknum = 25
    weekstart = int(time.time()) - 86400 * (time.localtime().tm_wday + 1)
    if weekstart < config.SEMESTER_BASE:
        weekstart = config.SEMESTER_BASE
    elif weekstart > config.SEMESTER_BASE + 25 * 7 * 86400:
        weekstart = config.SEMESTER_BASE + 25 * 7 * 86400
    startstr = time.strftime("%Y-%m-%d", time.localtime(weekstart))
    endstr = time.strftime("%Y-%m-%d", time.localtime(weekstart + 7 * 86400))

    duty_list = Duty.query.join(Activity).filter(Duty.uid == member_uid, Activity.start_time >= int(time.time())-30*86400).\
        order_by(Activity.start_time.desc())

    try:
        fp = open(config.BASE_DIR + 'cache/st_%s.log' % member_uid, 'r')
    except:
        pass#schedule_table = {}
        fp = open(config.BASE_DIR + 'cache/st_empty.log', 'r')

    for line in fp:
        timestr = line[:10]
        if timestr >= startstr and timestr < endstr:
            line = line.rstrip('\n')
            schedule_content = line[11:].split('\t')
            schedule_table[timestr] = schedule_content
    #print schedule_table
    if viewtype() == 1:
        return render_template('member/memberdetail_mobile.html', member=member)
    else:
        return render_template('member/memberdetail.html', member=member, schedule_table=schedule_table,
                               weekstart=weekstart, weeknum=weeknum, duty_list=duty_list)


@app.route('/membermanage-p<int:pagenum>')
@app.route('/membermanage')
@login_required
def membermanage(pagenum=1):
    """Page: all activitylist"""
    if not session.get('is_arra_monitor'):
        abort(403)
    member_count = Member.query.count()
    member_list = Member.query.order_by('convert(name using gb2312) ASC').limit(CONST.member_per_page).offset(CONST.member_per_page * (pagenum - 1))
    return render_template('member/membermanage.html',
        member_list=member_list,
        page_count=(member_count - 1) / CONST.member_per_page + 1, page_current=pagenum)


@app.route('/memberedit', methods=['GET', 'POST'])
@app.route('/memberedit-<member_uid>', methods=['GET', 'POST'])
@login_required
def memberedit(member_uid=''):

    if request.method == 'POST':
        form = MemberForm(request.form)
        if form.validate_on_submit():
            if not member_uid and Member.query.filter(Member.uid == form.uid.data).count():
                form.uid.errors.append('学号已存在')
            if Member.query.filter(Member.email == form.email.data, Member.uid != member_uid).count():
                form.email.errors.append('电子邮箱已存在')
            if Member.query.filter(Member.mobile_num == form.mobile_num.data, Member.uid != member_uid).count():
                form.mobile_num.errors.append('手机号码已存在')

        if not form.errors:
            member = Member.query.get(member_uid)
            if not session.get('is_arra_monitor'):
                abort(403)
            if not member:
                member = Member()
                member.uid = form.uid.data
                key = md5.new()
                key.update(form.mobile_num.data)
                member.password = key.hexdigest()
                member.update_register_time()
                member.update_lastlogin_time()
            else:
                member.uid = member_uid
            member.name = form.name.data
            member.sex = form.sex.data
            member.school = form.school.data
            member.mobile_num = form.mobile_num.data
            member.mobile_type = form.mobile_type.data
            member.mobile_short = form.mobile_short.data
            member.qqnum = form.qqnum.data
            member.email = form.email.data
            member.address = form.address.data
            member.credit_card = form.credit_card.data
            member.type = form.type.data
            member.introduce = form.introduce.data
            db.session.add(member)
            db.session.commit()

            flash({'type': 'success', 'content': '保存成功！'})
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
    flash({'type': 'success', 'content': '成员已删除。'})
    return redirect(url_for('membermanage'))


@app.route('/memberjson')
@login_required
def memberjson():
    member = Member.query.all()
    member_list = []
    for a in member:
        d = {'uid': a.uid, 'name': a.name, 'school': a.school}
        member_list.append(d)
    rtn = json.dumps(member_list)
    return rtn


@app.route('/memberactas-<member_uid>')
@login_required
def memberactas(member_uid):
    """Page: all activitylist"""
    if not session.get('is_arra_monitor'):
        abort(403)
    if member_uid == session.get('ori_uid'):
        session['uid'] = session['ori_uid']
        session['name'] = session['ori_name']
        session.pop('ori_uid', None)
        session.pop('ori_name', None)
    elif session.get('ori_uid'):
        member = Member.query.get_or_404(member_uid)
        session['uid'] = member_uid
        session['name'] = '[' + member.name + ']'
    else:
        member = Member.query.get_or_404(member_uid)
        session['ori_uid'] = session['uid']
        session['ori_name'] = session['name']
        session['uid'] = member_uid
        session['name'] = '[' + member.name + ']'
    flash({'type': 'success', 'content': '切换成功。'})
    return redirect('/member-' + member_uid)


@app.route('/memberexport')
@login_required
def memberexport():
    member_count = Member.query.count()
    member_list = Member.query.filter(Member.type==1).order_by('convert(name using gb2312) ASC')

    from acgweb.controller.export import export_member

    wb = export_member(member_list)
    tmp_filename = config.BASE_DIR + 'temp/member.xls'
    wb.save(tmp_filename)
    #if config.DEBUG: print tmp_filename
    response = send_file(tmp_filename, as_attachment=True, attachment_filename='member.xls')
    os.unlink(tmp_filename)
    return response

