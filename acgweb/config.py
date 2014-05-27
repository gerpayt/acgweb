# coding: utf-8
import acgweb.const as CONST

# Host
BASE_URL = 'http://acg.husteye.cn'
BASE_DIR = '/home/wwwroot/chenfeng/uwsgi/acgweb/acgweb/'
#HOST_STRING = 'root@1.1.1.1'

# App config
DEBUG = True
#os.urandom(16)
SECRET_KEY = '\xc8/\xf8\xf4\xbb\xb7\xbd\x15\x83;\x1e\xe2\x8d\x1a\xc2^'

PERMANENT_SESSION_LIFETIME = 3600*24*30

SESSION_COOKIE_NAME = 'acgweb_session'

# DB config
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "027idc"
DB_NAME = "chenfeng_acgweb"

# SMTP config
SMTP_SERVER = "smtp.exmail.qq.com"
SMTP_PORT = 25
SMTP_USE_TLS = False
SMTP_USE_SSL = False
SMTP_USER = "admin@nadc.cn"
SMTP_USERNAME = "Admin"
SMTP_PASSWORD = "supernadc612"


SEMESTER = '201302'

ARRA_MONITOR = ['M201371888','U201116111']

SEMASTER_BASE = 1392480000L
