# coding: utf-8

from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms import validators 


class RegisterForm(Form):
    username = TextField('username', description='学号', validators=[validators.DataRequired(message="学号不能为空")])
    password = PasswordField('password', description='密码', validators=[validators.DataRequired(message="密码不能为空")])
    password2 = PasswordField('password2', description='确认密码', validators=[validators.DataRequired(message="密码不能为空"), validators.EqualTo('password', message="两次密码不一致")])
    name = TextField('name', description='姓名', validators=[validators.DataRequired(message="姓名不能为空")])
    email = TextField('email', description='电子邮件', validators=[validators.DataRequired(message="电子邮件不能为空"), validators.Email(message="电子邮件格式错误")])
    mobile_num = TextField('mobile_num', description='手机号码', validators=[validators.DataRequired(message="手机号码不能为空")])
    reqcode = TextField('reqcode', description='邀请码', validators=[validators.DataRequired(message="邀请码不能为空")])
