# -- coding : utf-8 --
import sys
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from . import config

# convert python's encoding to utf8
reload(sys)
sys.setdefaultencoding('utf8')


app = Flask(__name__,template_folder='view')
app.config.from_pyfile('config.py')

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (
    config.DB_USER, config.DB_PASSWORD, config.DB_HOST, config.DB_NAME)
db = SQLAlchemy(app)

import model
import controller

