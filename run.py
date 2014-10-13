# coding: utf-8
from werkzeug.contrib.profiler import ProfilerMiddleware
from acgweb import app

#app.run(host='0.0.0.0',debug=True)
if __name__ == '__main__':
    if app.config['PROFILE']:
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    app.run(host='0.0.0.0')
application = app
