# coding: utf-8
from acgweb import db
import time


class Sign(db.Model):
    """Model for article"""
    id = db.Column(db.Integer, primary_key=True)
    act_name = db.Column(db.String(12))
    uid = db.Column(db.String(12))
    name = db.Column(db.String(12))
    group = db.Column(db.String(12))
    sign_time = db.Column(db.Integer)

    def __init__(self, sign_time=None):
        if sign_time is None:
            sign_time = int(time.time())
        self.sign_time = sign_time

    def __repr__(self):
        return '<Sign %s %s %s>' % (self.act_name, self.uid, self.name)
