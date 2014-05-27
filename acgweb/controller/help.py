# coding: utf-8
from flask import render_template, request, redirect, url_for, json, session, flash
from acgweb import app, db


@app.route('/help')
def help():
    """Page: all activitylist"""
    pass

    return render_template('help/index.html')
