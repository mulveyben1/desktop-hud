import psutil
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = ""
hostPort = 80
p = psutil.Process()
with p.oneshot():
    cpu_count = psutil.cpu_count(logical=True)
    total_mem = psutil.virtual_memory().total / 1073741824  # mem in GB
    c_size = psutil.disk_usage('C:\\').total / 1073741824
    d_size = psutil.disk_usage('D:\\').total / 1073741824
    f_size = psutil.disk_usage('F:\\').total / 1073741824
    g_size = psutil.disk_usage('G:\\').total / 1073741824
    i_size = psutil.disk_usage('I:\\').total / 1073741824


def get_sys_info():
    buffer = {}
    for i in range(0, cpu_count):
        buffer['cpu_%s' % i] = psutil.cpu_percent(interval=None, percpu=True)[i]
        time.sleep(0.1)
        buffer['cpu_%s' % i] = psutil.cpu_percent(interval=None, percpu=True)[i]
    buffer['total_mem'] = total_mem
    buffer['free_mem'] = psutil.virtual_memory().free / 1073741824
    buffer['c_size'] = c_size
    buffer['d_size'] = d_size
    buffer['f_size'] = f_size
    buffer['g_size'] = g_size
    buffer['i_size'] = i_size
    buffer['c_used'] = psutil.disk_usage('C:\\').used / 1073741824
    buffer['d_used'] = psutil.disk_usage('D:\\').used / 1073741824
    buffer['f_used'] = psutil.disk_usage('F:\\').used / 1073741824
    buffer['g_used'] = psutil.disk_usage('G:\\').used / 1073741824
    buffer['i_used'] = psutil.disk_usage('I:\\').used / 1073741824

    return buffer


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("%s" % get_sys_info(), "utf-8"))

    def do_POST(self):
        print("incomming http: ", self.path)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.send_response(200)


myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
