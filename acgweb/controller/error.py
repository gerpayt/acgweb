# coding: utf-8
from flask import render_template
from decorated_function import *
from acgweb import app


@app.errorhandler(404)
def error404(error):
    if viewtype() == 1:
        return render_template('site/error404_mobile.html'), 404
    else:
        return render_template('site/error404.html'), 404


@app.errorhandler(403)
def error403(error):
    if viewtype() == 1:
        return render_template('site/error403_mobile.html'), 403
    else:
        return render_template('site/error403.html'), 403


@app.errorhandler(500)
def error500(error):
    if viewtype() == 1:
        return render_template('site/error500_mobile.html'), 500
    else:
        return render_template('site/error500.html'), 500


@app.route('/error50x')
def error50x():
    raise SystemError
