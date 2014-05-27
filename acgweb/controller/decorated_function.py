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

