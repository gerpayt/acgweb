# coding: utf-8
import acgweb.const as CONST

# Host
BASE_URL = 'http://acg.husteye.cn'
BASE_DIR = '/home/wwwroot/chenfeng/uwsgi/acgweb/acgweb/'

# App config
DEBUG = True
#os.urandom(16)
SECRET_KEY = 'something^'

PERMANENT_SESSION_LIFETIME = 3600 * 24 * 30

SESSION_COOKIE_NAME = 'acgweb_session'

# DB config
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "acgweb"

# MAIL config
SMTP_SERVER = "smtp.exmail.qq.com"
SMTP_PORT = 25
SMTP_USE_TLS = False
SMTP_USE_SSL = False
IMAP_SERVER = "imap.exmail.qq.com"
IMAP_PORT = 25
SMTP_USER = ""
SMTP_USERNAME = ""
SMTP_PASSWORD = ""

SMS_PROVIDER = 'smsbao'
SMS_BASE_URL = 'http://www.smsbao.com/'
SMS_SEND_URL = 'sms?u={username}&p={password}&m={phone}&c={content}'
SMS_QUERY_URL = 'query?u={username}&p={password}'
SMS_USERNAME = ''
SMS_PASSWORD = ''

HTTP_PROXY = ''
MAIL_DOMAIN = 'acg-test'

SITE_TITLE = u'音控组管理系统'
README_TITLE = u"系统功能简介"

SEMESTER = '201302'

SYS_ADMIN = 'M201371888'

ARRA_MONITOR = ['M201371888']
TECH_MONITOR = ['M201371888']
DISC_MONITOR = ['M201371888']

SEMESTER_BASE = 1392480000L

REQCODE = '8888'

PROFILE = True
