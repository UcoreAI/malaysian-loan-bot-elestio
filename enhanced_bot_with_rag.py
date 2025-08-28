#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
print("DIAGNOSTIC BOT STARTING")
print(f"WhatsApp Token: {os.getenv('MALAYSIAN_LOAN_WHATSAPP_TOKEN')}")
print(f"OpenAI Key: {os.getenv('OPENAI_API_KEY')}")
class H(BaseHTTPRequestHandler):
    def do_GET(self):
          self.send_response(200)
          self.end_headers()
          self.wfile.write(b"Bot is running")
    def do_POST(self):
          print("WEBHOOK RECEIVED")
          data = self.rfile.read(int(self.headers['Content-Length']))
          print(f"Data: {data}")
          self.send_response(200)
          self.end_headers()
          self.wfile.write(b"OK")
s = HTTPServer(('0.0.0.0', 8080), H)
print("Server ready on port 8080")
s.serve_forever()
