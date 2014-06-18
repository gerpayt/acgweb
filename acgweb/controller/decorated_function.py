# coding: utf-8
from functools import wraps
from flask import render_template, request, redirect, url_for, session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('uid'):
            session['rtnurl']=request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def viewtype():
    vt = request.cookies.get('vt')
    if vt!=None:
        return int(vt)
    ua = request.headers.get('User-Agent').lower()
    #print ua
    re = 0
    osArr = {'iphone' : 1, 'ipad' : 1, 'ipod' : 1, 'android' : 2, 'windows phone' : 3}
    touchArr = {1 : ['safari', 'crios', 'ucbrowser', 'mqqbrowser'], 2 : ['chrome', 'ucbrowser', 'mqqbrowser'], 3 : ['ie']}
    for phone,k in osArr.items():
        if ua.find(phone)!=-1:
            for u in touchArr[k]:
                if ua.find(u)!=-1:
                    re = 1
                    break
            if re:
                break
    return re

