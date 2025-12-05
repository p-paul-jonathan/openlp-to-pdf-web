# Needed for deployment in GCP

import threading
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess

PORT = int(os.environ.get("PORT", 8080))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"worker alive")

def start_http_server():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()

def start_worker():
    subprocess.Popen(["rq", "worker", "openlp-jobs"]).wait()

if __name__ == "__main__":
    threading.Thread(target=start_http_server).start()
    start_worker()

