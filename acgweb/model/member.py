# coding: utf-8
from acgweb import db
from datetime import datetime
import time


class Member(db.Model):
    """Model for article"""
    uid = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(12), index=True)
    password = db.Column(db.String(32))
    type = db.Column(db.Integer)
    sex = db.Column(db.Integer)
    school = db.Column(db.String(12))
    mobile_num = db.Column(db.String(12))
    mobile_type = db.Column(db.Integer)
    mobile_short = db.Column(db.String(12))
    email = db.Column(db.String(32))
    qqnum = db.Column(db.String(32))
    address = db.Column(db.String(16))
    credit_card = db.Column(db.String(20))
    introduce = db.Column(db.Text)
    photo = db.Column(db.Text)
    register_time = db.Column(db.Integer)
    lastlogin_time = db.Column(db.Integer)
    flag = db.Column(db.Integer)
    setting = db.Column(db.Text)
    duties = db.relationship('Duty',
        backref=db.backref('owner', lazy='joined'))
    photos = []

    def __init__(self):
        '''self.uid = uid
        self.name = name
        self.password = password
        self.type = type
        self.sex = sex
        self.school = school
        self.mobile_num = mobile_num
        self.mobile_type = mobile_type
        self.mobile_short = mobile_short
        self.email = email
        self.qqnum = qqnum
        self.address = address
        self.credit_card = credit_card
        self.introduce = introduce'''
        self.sex = 0
        self.school = ''
        self.mobile_num = ''
        self.mobile_type = ''
        self.mobile_short = ''
        self.qqnum = ''
        self.address = ''
        self.credit_card = ''
        self.introduce = ''
        self.photo = ''
        self.register_time = 0
        self.lastlogin_time = 0
        self.flag = 0

    def getphotos(self):
        self.photos = self.photo.split('\n')
        return self.photos

    def appendphoto(self, url):
        self.photos.append(url)
        self.photo += "%s\n" % url

    def __repr__(self):
        return '<Member %s>' % self.name

    def update_register_time(self):
        self.register_time = int(time.time())

    def update_lastlogin_time(self):
        self.lastlogin_time = int(time.time())
