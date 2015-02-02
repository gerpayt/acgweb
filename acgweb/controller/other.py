# coding: utf-8
from flask import render_template, abort, flash
from acgweb import app
from acgweb.model.sign import Sign
from acgweb import config
from decorated_function import *


@app.route('/actsign-<act_name>')
def actsign(act_name=''):
    print act_name
    if act_name not in config.ACT_SIGNS:
        abort(404)
    sign_list = Sign.query.filter(Sign.act_name == act_name).order_by(Sign.sign_time.desc())
    status = 0
    for sign in sign_list:
        if session['uid']:
            if sign.uid == session['uid']:
                status = 1
                # login and signed
                break
            else:
                status = 2
                # login and not signed
                break
        elif session['sign-'+act_name]:
            if "%s:%s" % (sign.group, sign.name) == session['sign-'+act_name]:
                status = 3
                # not login and signed
                break
        else:
            status = 4
            # not login and not signed
            break
    print status
    return render_template('other/sign_mobile.html',
                           act_sign=config.ACT_SIGNS[act_name],
                           sign_list=sign_list,
                           status=status)
