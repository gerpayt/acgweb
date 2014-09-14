# coding: utf-8
from acgweb import db
from datetime import datetime
import time


class Duty(db.Model):
    """Model for duty"""
    id = db.Column(db.Integer, primary_key=True)
    aid = db.Column(db.Integer, db.ForeignKey('activity.id'), index=True)
    uid = db.Column(db.String(12), db.ForeignKey('member.uid'))
    status = db.Column(db.Integer)
    process = db.Column(db.Text)
    log = db.Column(db.Text)
    member = db.relationship('Member',
        backref=db.backref('duty', lazy='dynamic'))
    #activity = db.relationship('Activity',
    #    backref=db.backref('duty', lazy='dynamic'))
    processes = []
    logs = []

    def is_wait(self):
        return self.status in [2, 4]

    def is_abort(self):
        return self.status in [3, 5, 8, 9]

    def is_success(self):
        return self.status in [6, 7, 10, 11]

    def __repr__(self):
        return '<Duty %s>' % self.id

    def getlogs(self):
        self.logs = []
        #if not self.log: return []
        loglist = self.log.split('\n')
        for i in loglist:
            tmp = i.split('\t')
            if len(tmp) == 3:
                obj = {'time': tmp[0], 'type': tmp[1], 'content': tmp[2]}
                self.logs.append(obj)
        return self.logs

    def appendlog(self, type, content):
        self.logs.append({'time': int(time.time()), 'type': type, 'content': content})
        self.log += "%d\t%s\t%s\n" % (int(time.time()), type, content)

    def getprocesses(self):
        self.processes = []
        #if not self.process: return
        processlist = self.process.split('\n')
        for i in processlist:
            tmp = i.split('\t')
            if len(tmp) == 3:
                obj = {'time': tmp[0], 'op': tmp[1], 'content': tmp[2]}
                self.processes.append(obj)
        return self.processes

    def appendprocesse(self, op, content):
        if type(self.process) == type(None): self.process = ''
        self.processes.append({'time': int(time.time()), 'op': op, 'content': content})
        self.process += "%d\t%s\t%s\n" % (int(time.time()), op, content)
