# coding: utf-8
import md5

from flask import render_template, flash, jsonify, abort, make_response, json
from acgweb import app, db
from acgweb.model.member import Member
from acgweb.form.register import RegisterForm
from decorated_function import *
from acgweb import config
import os
from acgweb.controller import mail, sms


@app.route('/login', methods=['GET', 'POST'])
def weblogin():
    if request.method == 'POST':
        username = request.form['username'].upper()
        password = request.form['password']
        key = md5.new()
        key.update(password)
        member = Member.query.filter(Member.uid == username, Member.password == key.hexdigest()).first()
        #print user
        if member:
            if request.form.has_key('remberpassword'):
                session.permanent = True
            session['uid'] = username
            session['name'] = member.name
            session['is_arra_monitor'] = session['uid'] in config.ARRA_MONITOR
            url = session.get('rtnurl')
            member.update_lastlogin_time()
            db.session.add(member)
            db.session.commit()
            if not url: url = url_for('siteindex')
            session.pop('rtnurl', None)
            return redirect(url)
        else:
            flash({'type': 'error', 'content': '你提供的学号和密码不正确。'})
    if viewtype() == 1:
        return render_template('site/login_mobile.html')
    else:
        return render_template('site/login.html')


@app.route('/api/login')
def apilogin():
    username = request.args.get('username', '').upper()
    password = request.args.get('password', '')
    key = md5.new()
    key.update(password)
    member = Member.query.filter(Member.uid == username, Member.password == key.hexdigest()).first()
    #print user
    if member:
        import random
        access_token = str(random.randint(1000000000000000, 9999999999999999))
        res = {'uid': member.uid, 'name': member.name, 'access_token': access_token}
        member.update_lastlogin_time()
        member.access_token = access_token
        db.session.add(member)
        db.session.commit()
    else:
        res = {'error': '101', 'message': '你提供的学号和密码不正确。'}

    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/logout')
def weblogout():
    """Page: activity detail"""
    session.pop('uid', None)
    session.pop('name', None)
    session.pop('is_arra_monitor', None)
    session.clear()
    flash({'type': 'success', 'content': '注销成功。'})
    return redirect(url_for('login'))


@app.route('/api/logout')
@return_json
def apilogout(me):
    me.access_token = None
    db.session.add(me)
    db.session.commit()
    res = ({'message': '注销成功。'})
    return res


@app.route('/forgetpassword', methods=['GET', 'POST'])
def webforgetpassword():
    if request.method == 'POST':
        username = request.form['username'].upper()
        email = request.form['email']
        user = Member.query.filter(Member.uid == username, Member.email == email).first()
        if user:
            import random
            reset_password_token = str(random.randint(10000000, 99999999))
            session['reset_password_uid'] = username
            session['reset_password_token'] = reset_password_token
            url = config.BASE_URL + url_for('resetpassword', token=reset_password_token)
            subject = mail.webforgetpassword_tmpl['subject']
            content = mail.webforgetpassword_tmpl['content'] % (url, url)
            mail.send_mail(subject, content, username, email, touid=username, uid=username)
            flash({'type': 'success', 'content': '已经向邮箱中发送了电子邮件，请查收！'})
        else:
            flash({'type': 'error', 'content': '你提供的学号和电子邮件不正确。'})
    if viewtype() == 1:
        return render_template('site/forgetpassword_mobile.html')
    else:
        return render_template('site/forgetpassword.html')


@app.route('/api/forgetpassword')
def apiforgetpassword():
    username = request.args.get('username', '').upper()
    mobile = request.args.get('mobile', '')
    user = Member.query.filter(Member.uid == username, Member.mobile_num == mobile).first()
    if user:
        import random
        reset_password_token = str(random.randint(100000, 999999))
        user.reset_password_token = reset_password_token
        db.session.add(user)
        db.session.commit()
        content = sms.sms_forgetpassword_tmpl % reset_password_token
        sms.send_sms(mobile, content)
        res = {'success': True, 'message': '已经向手机中发送了验证码，请查收！'}
    else:
        res = {'error': '102', 'message': '你提供的学号和电子邮箱不正确。'}

    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/resetpassword-<token>', methods=['GET', 'POST'])
def webresetpassword(token=''):
    if request.method == 'POST':
        if session.has_key('reset_password_token') and session['reset_password_token'] == token:
            password = request.form['password']
            password_confirm = request.form['password_confirm']
            if not password:
                flash({'type': 'danger', 'content': '密码不能为空。'})
            elif password != password_confirm:
                flash({'type': 'danger', 'content': '两次密码不一致。'})
            else:
                uid = session['reset_password_uid']
                password = request.form['password']
                member = Member.query.get_or_404(uid)
                key = md5.new()
                key.update(password)
                member.password = key.hexdigest()
                db.session.add(member)
                db.session.commit()
                session.pop('reset_password_uid', None)
                session.pop('reset_password_token', None)
                flash({'type': 'success', 'content': '修改密码成功。'})
                return redirect(url_for('login'))
            if viewtype() == 1:
                return render_template('site/resetpassword_mobile.html')
            else:
                return render_template('site/resetpassword.html')
        else:
            abort(403)
    else:
        if session.has_key('reset_password_token') and session['reset_password_token'] == token:
            if viewtype() == 1:
                return render_template('site/resetpassword_mobile.html')
            else:
                return render_template('site/resetpassword.html')
        else:
            abort(403)


@app.route('/api/resetpassword')
def apiresetpassword():
    username = request.args.get('username', '').upper()
    reset_password_token = request.args.get('reset_password_token', '')
    password = request.args.get('password', '')
    if password:
        member = Member.query.filter(Member.uid == username, Member.reset_password_token == reset_password_token).first()
        if member:
            key = md5.new()
            key.update(request.form['password'])
            member.password = key.hexdigest()
            member.reset_password_token = None
            db.session.add(member)
            db.session.commit()
            res = {'success': True, 'message': '修改密码成功。'}
        else:
            res = {'error': '105', 'message': '你提供的验证码不正确。'}
    else:
        res = {'error': '106', 'message': '密码不能为空。'}

    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def webchangepassword():
    if request.method == 'POST':
        password_old = request.form['password_old']
        password_new = request.form['password_new']
        password_confirm = request.form['password_confirm']
        if not password_old:
            flash({'type': 'danger', 'content': '旧密码不能为空。'})
        elif not password_new:
            flash({'type': 'danger', 'content': '新密码不能为空。'})
        elif password_new != password_confirm:
            flash({'type': 'danger', 'content': '两次密码不一致。'})
        else:
            member = Member.query.get_or_404(session['uid'])
            key = md5.new()
            key.update(request.form['password_old'])
            if member.password != key.hexdigest():
                flash({'type': 'danger', 'content': '旧密码不正确。'})
                if viewtype() == 1:
                    return render_template('site/changepassword_mobile.html')
                else:
                    return render_template('site/changepassword.html')
            key = md5.new()
            key.update(request.form['password_new'])
            member.password = key.hexdigest()
            db.session.add(member)
            db.session.commit()
            flash({'type': 'success', 'content': '修改密码成功。'})
            return redirect(url_for('myinfo'))
        if viewtype() == 1:
            return render_template('site/changepassword_mobile.html')
        else:
            return render_template('site/changepassword.html')
    else:
        if viewtype() == 1:
            return render_template('site/changepassword_mobile.html')
        else:
            return render_template('site/changepassword.html')


@app.route('/api/changepassword')
@return_json
def apichangepassword(me):
    password_old = request.args.get('password_old', '')
    password_new = request.args.get('password_new', '')
    if not password_new:
        res = {'error': '110', 'content': '新密码不能为空。'}
    else:
        member = Member.query.get_or_404(me.uid)
        key = md5.new()
        key.update(password_old)
        if member.password != key.hexdigest():
            res = {'error': '111', 'content': '旧密码不正确。'}
        else:
            key = md5.new()
            key.update(password_new)
            member.password = key.hexdigest()
            db.session.add(member)
            db.session.commit()
            res = {'success': True, 'content': '修改密码成功。'}
    return res


@app.route('/register', methods=['GET', 'POST'])
def webregister():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.reqcode.data != config.REQCODE:
                form.reqcode.errors.append('邀请码错误')
            if Member.query.filter(Member.uid == form.username.data).count():
                form.username.errors.append('帐号已存在')
            if Member.query.filter(Member.email == form.email.data).count():
                form.email.errors.append('电子邮箱已存在')
            if Member.query.filter(Member.mobile_num == form.mobile_num.data).count():
                form.mobile_num.errors.append('手机号码已存在')
        if not form.errors:
            username = form.username.data
            password = form.password.data
            name = form.name.data
            email = form.email.data
            mobile = form.mobile_num.data
            register(username, password, name, email, mobile)
            flash({'type': 'success', 'content': '注册成功，请登陆。'})
            if viewtype() == 1:
                return render_template('site/login_mobile.html', form=form)
            else:
                return render_template('site/login.html', form=form)
    if viewtype() == 1:
        return render_template('site/register_mobile.html', form=form)
    else:
        return render_template('site/register.html', form=form)


@app.route('/api/register')
def apiregister():
    username = request.args.get('username', '').upper()
    password = request.args.get('password', '')
    name = request.args.get('name', '')
    email = request.args.get('email', '')
    mobile = request.args.get('mobile', '')
    reqcode = request.args.get('reqcode', '')
    errors = []
    if reqcode != config.REQCODE:
        errors.append('邀请码错误')
    if Member.query.filter(Member.uid == username).count():
        errors.append('帐号已存在')
    if Member.query.filter(Member.email == email).count():
        errors.append('电子邮箱已存在')
    if Member.query.filter(Member.mobile_num == mobile).count():
        errors.append('手机号码已存在')

    if not errors:
        register(username, password, name, email, mobile)
        res = {'success': True, 'message': '注册成功，请登陆。'}
    else:
        res = {'error': '120', 'message': json.dumps(errors)}
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def register(username, password, name, email, mobile):
    key = md5.new()
    key.update(password)
    member = Member()
    member.uid = username.upper()
    member.name = name
    member.password = key.hexdigest()
    member.email = email
    member.mobile_num = mobile
    member.type = 0
    member.update_register_time()
    member.update_lastlogin_time()
    db.session.add(member)
    db.session.commit()

    adminmember = Member.query.get(config.SYS_ADMIN)
    readmeurl = config.BASE_URL + url_for('articledetail', article_title=config.README_TITLE)
    admin_url = config.BASE_URL + url_for('memberdetail', member_uid=config.SYS_ADMIN)
    admin_name = adminmember.name
    subject = mail.register_tmpl['subject']
    content = mail.register_tmpl['content'] % (readmeurl, readmeurl, admin_url, admin_name)
    msg_id = mail.send_message(member.uid, config.SYS_ADMIN, subject, content, 2)
    mail.send_mail(subject, content, member.name, member.email,
                   msgid=msg_id, touid=member.uid, uid=member.uid)


@app.route('/imageupload', methods=['POST'])
@login_required
def imageupload():
    from werkzeug.utils import secure_filename
    file = request.files['Filedata']
    if file:
        member = Member.query.get(session['uid'])
        filename = secure_filename(file.filename)
        ori_filename = filename
        i = 1
        while os.path.exists(os.path.join(config.BASE_DIR, "data/member", filename)):
            filename = ori_filename[:ori_filename.rfind('.')] + '_' + str(i) + ori_filename[ori_filename.rfind('.'):]
            i += 1
            #print filename
        tmp_filename = config.BASE_DIR + 'temp/temp_image'
        #file.save(os.path.join(CONST.member_image_folder, tmp_filename))
        '''try:
            from PIL import Image
            im = Image.open(tmp_filename)
            size = im.size
            if size[1]>600:
                new_size = (600*size[1]/size[0],600)
            else:
                new_size = size
            im_resized = im.resize(new_size, Image.ANTIALIAS)
            im_resized.save(os.path.join(CONST.member_image_folder, filename))
        except: '''
        # TODO PIL decoder jpeg not available

        file.save(os.path.join(config.BASE_DIR, "data/member", filename))
        member.getphotos()
        member.appendphoto("data/member/%s" % filename)
        db.session.add(member)
        db.session.commit()
        return "data/member/%s" % filename
    return jsonify(error='error', msg='失败')


@app.route('/imagedelete', methods=['POST'])
@login_required
def imagedelete():
    url = request.form['url']
    if url:
        if os.path.exists(os.path.join(config.BASE_DIR, url)):
            os.unlink(os.path.join(config.BASE_DIR, url))
        member = Member.query.get(session['uid'])
        photolist = member.photo.split('\n')
        # more pythonic
        new_photo_list = filter(lambda x: x and x != url, photolist)
        #print url,photolist,new_photo_list
        member.photo = ''
        for i in new_photo_list:
            member.photo += i + '\n'
        db.session.add(member)
        db.session.commit()
    return ''


@app.route('/set-<key>-<value>')
@app.route('/set-<key>')
@login_required
def set(key, value=None):
    """Page: all articles"""
    referer = request.referrer
    if not referer:
        referer = url_for('index')

    if value == None:
        response = make_response(redirect(referer))
        response.set_cookie(key, expires=0)
    else:
        response = make_response(redirect(referer))
        response.set_cookie(key, value)
    return response
