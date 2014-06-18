# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, flash
from acgweb import app, db
from decorated_function import *


@app.route('/help')
def help():
    """Page: all activitylist"""
    pass

    if viewtype()==1:
        return render_template('help/index_mobile.html')
    else:
        return render_template('help/index.html')
