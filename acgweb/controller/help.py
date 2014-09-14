# coding: utf-8
from flask import render_template
from acgweb import app
from decorated_function import *


@app.route('/help')
def help():
    """Page: all activitylist"""
    pass

    if viewtype() == 1:
        return render_template('help/index_mobile.html')
    else:
        return render_template('help/index.html')
