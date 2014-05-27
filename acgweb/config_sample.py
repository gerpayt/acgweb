# coding: utf-8
import acgweb.const as CONST

# Host
BASE_URL = 'http://acg.husteye.cn'
BASE_DIR = '/home/wwwroot/chenfeng/uwsgi/acgweb/acgweb/'

# App config
DEBUG = True
#os.urandom(16)
SECRET_KEY = 'something^'

PERMANENT_SESSION_LIFETIME = 3600*24*30

SESSION_COOKIE_NAME = 'acgweb_session'

# DB config
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "acgweb"

# SMTP config
SMTP_SERVER = ""
SMTP_PORT = 25
SMTP_USE_TLS = False
SMTP_USE_SSL = False
SMTP_USER = ""
SMTP_USERNAME = ""
SMTP_PASSWORD = ""

HTTP_PROXY = ''

SEMESTER = '201302'

ARRA_MONITOR = ['M201371888','U201116111']

SEMASTER_BASE = 1392480000L

