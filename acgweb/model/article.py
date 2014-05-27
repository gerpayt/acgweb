# coding: utf-8
from acgweb import db
import time

class Article(db.Model):
    """Model for article"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), index = True, unique = True)
    cate_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    posttime = db.Column(db.Integer)


    def __init__(self, posttime=None):
        if posttime is None:
            posttime = int(time.time())
        self.posttime = posttime

    def __repr__(self):
        return '<Article %s>' % self.name

