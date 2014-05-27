# coding: utf-8
from acgweb import db
import acgweb.config

class Schedule(db.Model):
    """Model for duty"""
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(12), db.ForeignKey('member.uid'))
    semester = db.Column(db.String(8))
    week = db.Column(db.String(16))
    weekday = db.Column(db.String(8))
    section = db.Column(db.String(8))
    classname = db.Column(db.String(8))
    classtype = db.Column(db.Integer)

    def __repr__(self):
        return '<Schedule %s>' % self.id

    def update_semester(self):
        self.semester = acgweb.config.SEMESTER

    def strtolist(self):
        self.weeklist =_parsemystr(self.week)
        self.weekdaylist =_parsemystr(self.weekday)
        self.sectionlist =_parsemystr(self.section)


def _parsemystr(str):
    rtnlist = []
    tmp1 = str.split(',')
    print 'tmp1',tmp1
    for i in tmp1:
        tmp2 = i.split('-');
        print i,'tmp2',tmp2
        if len(tmp2)==2:
            for j in range (int(tmp2[0]),int(tmp2[1])+1):
                rtnlist.append(j)
        else:
            rtnlist.append(i)
    return rtnlist