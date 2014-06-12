# coding: utf-8

from flask_wtf import Form
from wtforms import TextField,SelectField,TextAreaField,HiddenField
from wtforms import validators 
import acgweb.const as CONST

class DutyForm(Form):
    id = HiddenField('id')
    aid = TextField('aid', description='活动ID', validators=[validators.DataRequired(message="活动ID不能为空")])
    uid = TextField('uid', description='用户ID', validators=[validators.DataRequired(message="用户ID不能为空")])
    status = SelectField('status', description='值班状态',coerce=int, choices=zip(range(len(CONST.dutystatusname)),CONST.dutystatusname))
    processstr = TextAreaField('process', description='流程')
    logstr = TextAreaField('log', description='记录')




