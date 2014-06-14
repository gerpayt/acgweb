# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, flash, jsonify, abort
from acgweb import app, db
from acgweb.model.member import Member
from acgweb.form.register import RegisterForm
import acgweb.const as CONST
import template_filter
from decorated_function import *
from acgweb import config
import os,md5
from acgweb.controller import mail


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page: all activitylist"""
    if request.method == 'POST':
        username = request.form['username'].upper()
        password = request.form['password']
        key = md5.new()
        key.update(password)
        member = Member.query.filter(Member.uid==username, Member.password==key.hexdigest()).first()
        #print user
        if member:
            session['uid'] = username
            session['name'] = member.name
            session['is_arra_monitor'] = session['uid'] in config.ARRA_MONITOR
            url = session.get('rtnurl')
            member.update_lastlogin_time()
            db.session.add(member)
            db.session.commit()
            if not url: url = url_for('siteindex')
            session.pop('rtnurl',None)
            return redirect(url)
        else:
            flash({'type':'error', 'content':'你提供的学号和密码不正确。'})
    if viewtype()==1:
        return render_template('site/login_mobile.html')
    else:
        return render_template('site/login.html')

@app.route('/logout')
def logout():
    """Page: activity detail"""
    session.pop('uid',None)
    session.pop('name',None)
    flash({'type':'success', 'content':'注销成功。'})
    return redirect(url_for('login'))

@app.route('/forgetpassword', methods=['GET', 'POST'])
def forgetpassword():
    """Page: activity detail"""
    if request.method == 'POST':
        username = request.form['username'].upper()
        email = request.form['email']
        user = Member.query.filter(Member.uid==username, Member.email==email).first()
        if user:
            import random
            token = str(random.randint(10000000,99999999))
            session['reset_password_uid'] = username
            session['reset_password_token'] = token
            url = config.BASE_URL + url_for('resetpassword',token=token)
            subject = mail.forgetpassword_tmpl['subject']
            content = mail.forgetpassword_tmpl['content'] % ( url , url )
            mail.send_mail(subject, content, username, email)
            #subject,content,toname,toemail
            flash({'type':'success', 'content':'已经向邮箱中发送了电子邮件，请查收！'})
        else:
            flash({'type':'error', 'content':'你提供的学号和电子邮件不正确。'})
    if viewtype()==1:
        return render_template('site/forgetpassword_mobile.html')
    else:
        return render_template('site/forgetpassword.html')


@app.route('/resetpassword-<token>', methods=['GET', 'POST'])
def resetpassword(token=''):
    """Page: activity detail"""
    if request.method == 'POST':
        if session.has_key('reset_password_token') and session['reset_password_token'] == token:
            password = request.form['password']
            password_confirm = request.form['password_confirm']
            if not password:
                flash({'type':'danger', 'content':'密码不能为空。'})
            elif password != password_confirm:
                flash({'type':'danger', 'content':'两次密码不一致。'})
            else:
                member = Member.query.get_or_404(session['reset_password_uid'])
                key = md5.new()
                key.update(request.form['password'])
                member.password=key.hexdigest()
                db.session.add(member)
                db.session.commit()
                session.pop('reset_password_uid',None)
                session.pop('reset_password_token',None)
                flash({'type':'success', 'content':'修改密码成功。'})
                return redirect(url_for('login'))
            if viewtype()==1:
                return render_template('site/resetpassword_mobile.html')
            else:
                return render_template('site/resetpassword.html')
        else:
            abort(403)
    else:
        if session.has_key('reset_password_token') and session['reset_password_token'] == token:
            if viewtype()==1:
                return render_template('site/resetpassword.html')
            else:
                return render_template('site/resetpassword.html')
        else:
            abort(403)


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def changepassword():
    """Page: activity detail"""
    if request.method == 'POST':
        password_old = request.form['password_old']
        password_new = request.form['password_new']
        password_confirm = request.form['password_confirm']
        if not password_old:
            flash({'type':'danger', 'content':'旧密码不能为空。'})
        elif not password_new:
            flash({'type':'danger', 'content':'新密码不能为空。'})
        elif password_new != password_confirm:
            flash({'type':'danger', 'content':'两次密码不一致。'})
        else:
            member = Member.query.get_or_404(session['uid'])
            key = md5.new()
            key.update(request.form['password_old'])
            if member.password != key.hexdigest():
                flash({'type':'danger', 'content':'旧密码不正确。'})
                return render_template('site/changepassword.html')
            key = md5.new()
            key.update(request.form['password_new'])
            member.password = key.hexdigest()
            db.session.add(member)
            db.session.commit()
            flash({'type':'success', 'content':'修改密码成功。'})
            return redirect(url_for('myinfo'))
        return render_template('site/changepassword.html')
    else:
        return render_template('site/changepassword.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page: activity detail"""
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.reqcode.data != config.REQCODE:
                form.reqcode.errors.append('邀请码错误')
            if Member.query.filter(Member.uid==form.username.data).count():
                form.username.errors.append('帐号已存在')
            if Member.query.filter(Member.email==form.email.data).count():
                form.email.errors.append('电子邮箱已存在')
            if Member.query.filter(Member.mobile_num==form.mobile_num.data).count():
                form.mobile_num.errors.append('手机号码已存在')
        if not form.errors:
            key = md5.new()
            key.update(form.password.data)
            member = Member()
            member.uid=form.username.data.upper()
            member.name=form.name.data
            member.password=key.hexdigest()
            member.email=form.email.data
            member.mobile_num=form.mobile_num.data
            member.type=0
            member.update_register_time()
            member.update_lastlogin_time()
            db.session.add(member)
            db.session.commit()

            adminmember = Member.query.get(config.SYS_ADMIN)
            readmeurl = url_for('articledetail',article_title=config.README_TITLE)
            admin_url = url_for('memberdetail',member_uid=config.SYS_ADMIN)
            admin_name = adminmember.name
            subject = mail.register_tmpl['subject']
            content = mail.register_tmpl['content'] % ( readmeurl, readmeurl, admin_url, admin_name )
            msg_id = mail.send_message(member.uid,config.SYS_ADMIN,subject,content,2)
            mail.send_mail(subject, content, member.name, member.email,
                msgid=msg_id)

            flash({'type':'success', 'content':'注册成功，请登陆。'})
            if viewtype()==1:
                return render_template('site/login_mobile.html',form=form)
            else:
                return render_template('site/login.html',form=form)
    if viewtype()==1:
        return render_template('site/register_mobile.html',form=form)
    else:
        return render_template('site/register.html',form=form)


@app.route('/imageupload', methods=['POST'])
@login_required
def imageupload():
    from werkzeug.utils import secure_filename
    file = request.files['Filedata']
    if file :
        member = Member.query.get(session['uid'])
        filename = secure_filename(file.filename)
        ori_filename = filename
        i=1
        while os.path.exists(os.path.join(config.BASE_DIR, "data/member", filename)):
            filename = ori_filename[:ori_filename.rfind('.')]+'_'+str(i)+ori_filename[ori_filename.rfind('.'):]
            i+=1
            #print filename
        tmp_filename = config.BASE_DIR+'temp/temp_image'
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
    return jsonify(error='error',msg='失败')


@app.route('/imagedelete', methods=['POST'])
@login_required
def imagedelete():
    url = request.form['url']
    if url :
        if os.path.exists(os.path.join(config.BASE_DIR, url)):
            os.unlink(os.path.join(config.BASE_DIR, url))
        member = Member.query.get(session['uid'])
        photolist = member.photo.split('\n')
        # more pythonic
        new_photo_list = filter(lambda x: x and x!= url, photolist)
        #print url,photolist,new_photo_list
        member.photo = ''
        for i in new_photo_list:
            member.photo += i+'\n'
        db.session.add(member)
        db.session.commit()
    return '';
