# coding: utf-8

from flask_wtf import Form
from wtforms import TextField, SelectField, HiddenField
from wtforms import validators 
import acgweb.const as CONST


class ArticleForm(Form):
    id = HiddenField('id')
    title = TextField('title', description='文章名称', validators=[validators.DataRequired(message="文章名称不能为空")])
    cate_id = SelectField('cate_id', description='文章分类', coerce=int, choices=CONST.categorysellect)
    content = TextField('content', description='内容')
