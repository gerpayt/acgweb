# coding: utf-8
from acgweb import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import case
from datetime import datetime
from acgweb import config
import acgweb.const as CONST
import time


class Activity(db.Model):
    """Model for article"""
    id = db.Column(db.Integer, primary_key=True)
    #oid = db.Column(db.Integer, unique=True)
    title = db.Column(db.String(32), index=True)
    remark = db.Column(db.Text)
    venue = db.Column(db.Integer)
    work_start_time = db.Column(db.Integer)
    start_time = db.Column(db.Integer)
    end_time = db.Column(db.Integer)
    type = db.Column(db.Integer)
    hostname = db.Column(db.String(32))
    duties = db.relationship('Duty',
        backref=db.backref('activity', lazy='joined'))
    status = db.Column(db.Integer)
    _strustarttime = {}

    def __repr__(self):
        return '<Activity %s %f>' % (self.title, self.last_time)

    @hybrid_property
    def last_time(self):
        if self.end_time:
            return (1.0 * self.end_time - self.start_time) / 3600
        else:
            return 0.0

    def work_last_time(self):
        if self.end_time:
            return (1.0 * self.end_time - self.work_start_time) / 3600
        else:
            return 0.0

#    def work_start_time(self):
#        return self.start_time - 3600

    def from_time(self):
        secs = self.start_time - int(time.time())
        return secs
        #if secs>0:
        #    (day,hour) = divmod(secs,86400)
        #    (hour,min) = divmod(hour,3600)
        #    (min,sec) = divmod(min,60)
        #    return '%d天%d小时%d分%d秒' % (day,hour,min,sec)

    def getstrustarttime(self):
        if not self._strustarttime:
            offset = self.start_time - config.SEMESTER_BASE
            (week, weekday) = divmod(offset, 7 * 86400)
            (weekday, sec) = divmod(weekday, 86400)
            hour = sec / 3600
            if hour >= 6 and hour <= 10:
                start_section = 1
            elif hour >= 11 and hour <= 13:
                start_section = 3
            elif hour >= 14 and hour <= 16:
                start_section = 5
            elif hour >= 17 and hour <= 18:
                start_section = 7
            elif hour >= 19 and hour <= 22:
                start_section = 9
            self._strustarttime = {'week': int(week) + 1, 'weekday': int(weekday), 'start_section': int(start_section)}
        return self._strustarttime;
