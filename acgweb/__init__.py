# coding: utf-8
import sys
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from . import config
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

# convert python's encoding to utf8
reload(sys)
sys.setdefaultencoding('utf8')


app = Flask(__name__, template_folder='view')
app.config.from_pyfile('config.py')

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (
    config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_NAME)
app.config['SQLALCHEMY_POOL_RECYCLE'] = 5
db = SQLAlchemy(app)

file_handler = RotatingFileHandler('./acgweb/log/error.log', 'a', 1 * 1024 * 1024, 10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

import model
import controller
