import signal
import commands
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

port = 7709


class PullHTTPHandle(BaseHTTPRequestHandler):
    def do_GET(self):
        buf = "WebHook Works! Please do POST Action."
        self.protocal_version = "HTTP/1.1"
        self.send_response(200)
        self.end_headers()
        self.wfile.write(buf)

    def do_POST(self):
        self.protocal_version = "HTTP/1.1"
        ua = self.headers['user-agent'] if 'user-agent' in self.headers else ''
        if 'GitHub-Hookshot/' in ua:
            res = self.do_PULL()
            code = 200
            buf = "Success!\r\n" + res
        else:
            code = 403
            buf = "Forbidden"
        self.send_response(code)
        self.end_headers()
        self.wfile.write(buf)

    def do_PULL(self):
        cmd = 'git pull'
        (status, output) = commands.getstatusoutput(cmd)
        return output


signal.signal(signal.SIGINT, lambda x,y:exit(1))

http_server = HTTPServer(('127.0.0.1', int(port)), PullHTTPHandle)
http_server.serve_forever()

