# coding: utf-8

from flask_wtf import Form
from wtforms import TextField,HiddenField,SelectField
from wtforms import validators 
import acgweb.const as CONST

class ScheduleForm(Form):
    id        = HiddenField('id')
    classname = TextField  ('classname', description='课程名称', validators=[validators.DataRequired(message="课程名称不能为空")])
    classtype = SelectField('classtype', coerce=int, description='课程类型', validators=[validators.DataRequired(message="必选")],
        choices=zip(range(len(CONST.classtypename)),CONST.classtypename))
    week      = TextField  ('week',      description='周次',     validators=[validators.DataRequired(message="周次不能为空")])
    weekday   = TextField  ('weekday',   description='周天',     validators=[validators.DataRequired(message="不能为空")])
    section   = TextField  ('section',   description='节次',     validators=[validators.DataRequired(message="不能为空")])

    #def validate_name(form, field):
    #    if len(field.data) > 50:
    #        raise ValidationError('Name must be less than 50 characters')
