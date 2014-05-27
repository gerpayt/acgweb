# coding: utf-8

from flask_wtf import Form
from wtforms import TextField,SelectField,TextAreaField,HiddenField
from wtforms import validators 
import acgweb.const as CONST

class MemberForm(Form):
    uid = TextField('uid', description='学号')
    name = TextField('name', description='姓名', validators=[validators.DataRequired(message="姓名不能为空")])
    sex = SelectField('sex', description='性别', coerce=int, choices=zip(range(len(CONST.sexname)),CONST.sexname))
    school = TextField('name', description='专业')
    mobile_num = TextField('mobile_num', description='手机号码', validators=[validators.DataRequired(message="手机号码不能为空")])
    mobile_type = SelectField('mobile_type', coerce=int, description='手机类型', choices=zip(range(len(CONST.mobiletypename)),CONST.mobiletypename))
    mobile_short = TextField('mobile_short', description='手机短号')
    qqnum = TextField('qqnum', description='QQ号')
    email = TextField('email', description='电子邮件', validators=[validators.DataRequired(message="电子邮件不能为空"),validators.Email(message="电子邮件格式错误")])
    address = TextField('address', description='住址')
    credit_card = TextField('credit_card', description='银行卡号')
    type = SelectField('type', description='类型', coerce=int, choices=zip(range(len(CONST.membertypename)),CONST.membertypename))
    
    introduce = TextAreaField('introduce', description='个人简介')
    photo = HiddenField('photo')

