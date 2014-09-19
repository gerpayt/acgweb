# -- coding:utf-8 --
import sys
sys.path.append("../acgweb")
from acgweb import app
from acgweb import config
import unittest
import re

class acgwebTestCase(unittest.TestCase):

    def setUp(self):
        print 'test start ...'
        #acgweb.app.config['SQLALCHEMY_DATABASE_URI'] =
        self.app = app.test_client()

    def tearDown(self):
        print 'test finished.'

    def login(self, username, password):
        return self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def register(self, username, password, name, email, mobile_num, reqcode):
        rv = self.app.get('/register')
        #print rv.data
        rexp = '<input id=\"csrf_token\" name=\"csrf_token\" type=\"hidden\" value=\"(.*)\">'
        match = re.search(rexp, rv.data)
        csrf_token = match.group(1)
        assert match is not None
        return self.app.post('/register', data=dict(username=username, password=password, password2=password,
            name=name, email=email, mobile_num=mobile_num, reqcode=reqcode, csrf_token=csrf_token), follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        #print rv.data
        assert '你提供的学号和密码不正确。' in rv.data

        rv = self.login('M201371888', 'admin')
        #print rv.data
        assert '你提供的学号和密码不正确。' not in rv.data
        assert '<li><a href="/manage">管理</a></li>' in rv.data

        rv = self.logout()
        #print rv.data
        assert '注销成功。' in rv.data

    def test_register(self):
        rv = self.register('', '', '', '', '', '')
        #print rv.data
        assert '学号不能为空' in rv.data
        assert '密码不能为空' in rv.data
        assert '姓名不能为空' in rv.data
        assert '电子邮件不能为空' in rv.data
        assert '手机号码不能为空' in rv.data
        assert '邀请码不能为空' in rv.data

        rv = self.register('M201371888', 'password', 'cf', 'gerpayt@qq.com', '15271810369', config.REQCODE)
        #print rv.data
        assert '帐号已存在' in rv.data
        assert '电子邮箱已存在' in rv.data
        assert '手机号码已存在' in rv.data

        # TODO

    def test_task_process(self):
        # activity user apply
        rv = self.login('M201371888', 'admin')
        print dir(rv)

        rv = self.app.get('/')
        print rv.data

if __name__ == '__main__':
    unittest.main()
