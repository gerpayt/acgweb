# coding: utf-8
from acgweb import db
import time


class Message(db.Model):
    """Model for duty"""
    id = db.Column(db.Integer, primary_key=True)
    fromuid = db.Column(db.String(12), db.ForeignKey('member.uid'))
    touid = db.Column(db.String(12), db.ForeignKey('member.uid'))
    subject = db.Column(db.String(8))
    content = db.Column(db.Text)
    sendtime = db.Column(db.Integer)
    readtime = db.Column(db.Integer)
    type = db.Column(db.Integer)
    status = db.Column(db.Integer)
    frommember = db.relationship('Member', foreign_keys=fromuid,
        backref=db.backref('msgfrom', lazy='dynamic'))
    tomember = db.relationship('Member', foreign_keys=touid,
        backref=db.backref('msgto', lazy='dynamic'))

    def __init__(self, sendtime=None, readtime=None):
        if sendtime is None:
            sendtime = int(time.time())
        self.sendtime = sendtime
        if readtime is None:
            readtime = 0
        self.readtime = 0

    def __repr__(self):
        return '<Message %s>' % self.id

    def update_sendtime(self):
        self.sendtime = int(time.time())

    def update_readtime(self):
        if not self.readtime:
            self.readtime = int(time.time())
