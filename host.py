import psutil
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = ""
hostPort = 8080
p = psutil.Process()
with p.oneshot():
    cpu_count = psutil.cpu_count(logical=True)
    total_mem = psutil.virtual_memory().total / 1073741824  # mem in GB
    numdisks = len(list(psutil.disk_partitions()))
    parts = {}
    for part in psutil.disk_partitions():
        parts['%s' % part.mountpoint] = part


def get_sys_info():
    buffer = {}
    for i in range(0, cpu_count):
        buffer['cpu_%s' % i] = psutil.cpu_percent(interval=None, percpu=True)[i]
        time.sleep(0.1)
        buffer['cpu_%s' % i] = psutil.cpu_percent(interval=None, percpu=True)[i]
    buffer['total_mem'] = total_mem
    buffer['free_mem'] = psutil.virtual_memory().available / 1073741824
    for part in parts.keys():
        buffer['size_%s' % part] = psutil.disk_usage('%s' % part).total / 1073741824
        buffer['used_%s' % part] = psutil.disk_usage('%s' % part).used / 1073741824
    buffer['numdisks'] = numdisks

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
