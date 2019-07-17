from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class SimpleServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>GET!</h1></body></html>".encode())
        return

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


server = ThreadedHTTPServer(('', 8080), SimpleServer)
thread = threading.Thread(target=server.serve_forever)
thread.daemon = True
