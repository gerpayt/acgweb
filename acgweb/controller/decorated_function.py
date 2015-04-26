# coding: utf-8
from functools import wraps

from flask import request, redirect, url_for, session
from acgweb.model.member import Member


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('uid'):
            session['rtnurl'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def viewtype():
    vt = request.cookies.get('vt')
    if vt is not None:
        return int(vt)
    ua = request.headers.get('User-Agent')
    if ua:
        ua = ua.lower()
    else:
        ua = ''
    mobile_ua = ['iphone', 'android', 'windows phone']
    #print ua
    for u in mobile_ua:
        if ua.find(u) != -1:
            return 1
    return 0


def return_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import json, make_response
        from acgweb.model.member import Member

        access_token = request.args.get('access_token', '0')
        me = Member.query.filter(Member.access_token == access_token).first()
        if me:
            res = f(me, *args, **kwargs)
        else:
            res = {'error': '110', 'message': 'token不正确或者已经过期。'}
        resp = make_response(json.dumps(res))
        resp.headers['Content-Type'] = 'application/json; charset=utf-8'
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    return decorated_function
