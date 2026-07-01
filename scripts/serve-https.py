"""Serve o frontend com HTTPS usando certificados mkcert."""
import http.server
import os
import ssl
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8443
CERTS_DIR = os.path.join(os.path.dirname(__file__), "..", ".certs")
CERT = os.path.abspath(os.path.join(CERTS_DIR, "dev-cert.pem"))
KEY = os.path.abspath(os.path.join(CERTS_DIR, "dev-key.pem"))
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "frontend-webapp"))

os.chdir(FRONTEND_DIR)
httpd = http.server.HTTPServer(("0.0.0.0", PORT), http.server.SimpleHTTPRequestHandler)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain(CERT, KEY)
httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
print(f"Serving frontend at https://localhost:{PORT}")
httpd.serve_forever()
