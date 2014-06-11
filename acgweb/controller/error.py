# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, flash
from decorated_function import *
from acgweb import app, db


@app.errorhandler(404)
def error404(error):
    if viewtype()==1:
        return render_template('site/error404_mobile.html'), 404
    else:
        return render_template('site/error404.html'), 404

@app.errorhandler(403)
def error403(error):
    if viewtype()==1:
        return render_template('site/error403_mobile.html'), 401
    else:
        return render_template('site/error403.html'), 401
