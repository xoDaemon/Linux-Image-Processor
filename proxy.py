import http.server
import socketserver
import urllib.request

PORT = 8080

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/proxy/'):
            url = self.path[7:]
            print(url)
            try:
                with urllib.request.urlopen(url) as response:
                    self.send_response(response.status)
                    for key, value in response.headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(response.read())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

Handler = Proxy

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()