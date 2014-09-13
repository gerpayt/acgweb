# coding: utf-8

from flask_wtf import Form
from wtforms import TextField,SelectField,TextAreaField,HiddenField
from wtforms import validators 
import acgweb.const as CONST
import time



class ActivityForm(Form):
    id = HiddenField('id')
    title = TextField('title', description='活动名称', validators=[validators.DataRequired(message="活动名称不能为空")])
    remark = TextAreaField('remark', description='注释')
    venue = SelectField('venue', coerce=int, description='场地', choices=zip(range(len(CONST.venuename)),CONST.venuename))
    #date_str = DateField('date_str', description='活动日期', validators=[validators.DataRequired(message="开始时间不能为空")], format='%Y-%m-%d')
    work_start_time = HiddenField('work_start_time', description='值班时间', validators=[validators.DataRequired(message="值班时间不能为空")])
    start_time = HiddenField('start_time', description='开始时间', validators=[validators.DataRequired(message="开始时间不能为空")])
    end_time = HiddenField('end_time', description='结束时间')
    type = SelectField('type', coerce=int, description='活动类型', choices=zip(range(len(CONST.activitytypename)),CONST.activitytypename))
    status = SelectField('status', coerce=int, description='活动状态', choices=zip(range(len(CONST.activitystatusname)),CONST.activitystatusname))
    
    hostname = TextField('introduce', description='主办法')

