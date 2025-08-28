#!/usr/bin/env python3
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

print("DIAGNOSTIC BOT STARTING")
print(f"WhatsApp Token: {'SET' if os.getenv('MALAYSIAN_LOAN_WHATSAPP_TOKEN') else 'MISSING'}")
print(f"OpenAI Key: {'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING'}")

class DiagnosticBot:
def __init__(self):
          self.whatsapp_token = os.getenv('MALAYSIAN_LOAN_WHATSAPP_TOKEN')
          self.openai_key = os.getenv('OPENAI_API_KEY')

def process_webhook(self, webhook_data):
          print("WEBHOOK RECEIVED:")
          print(json.dumps(webhook_data, indent=2))
          try:
              messages = webhook_data.get('messages', [])
              if not messages:
                  return {"status": "no_message"}
              message = messages[0]
              if message.get('from_me', False):
                  return {"status": "ignored"}
              phone_number = message.get('from', '')
              message_text = message.get('text', {}).get('body', '')
              print(f"Phone: {phone_number}")
              print(f"Message: {message_text}")
              if not self.whatsapp_token:
                  print("NO WHATSAPP TOKEN!")
                  return {"status": "no_token"}
              print("Would send response")
              return {"status": "diagnostic_complete"}
          except Exception as e:
              print(f"ERROR: {e}")
              return {"status": "error"}

  bot = DiagnosticBot()

  class WebhookHandler(BaseHTTPRequestHandler):
  def do_POST(self):
  if self.path in ['/webhook', '/client/001/webhook']:
              length = int(self.headers['Content-Length'])
              data = json.loads(self.rfile.read(length))
              result = bot.process_webhook(data)
              self.send_response(200)
              self.send_header('Content-type', 'application/json')
              self.end_headers()
              self.wfile.write(json.dumps(result).encode())
  else:
              self.send_response(404)
              self.end_headers()

  def do_GET(self):
  if self.path == '/health':
              health = {"status": "diagnostic", "token": bool(bot.whatsapp_token)}
              self.send_response(200)
              self.send_header('Content-type', 'application/json')
              self.end_headers()
              self.wfile.write(json.dumps(health).encode())
  else:
              self.send_response(200)
              self.send_header('Content-type', 'text/html')
              self.end_headers()
              self.wfile.write(b"<h1>Diagnostic Bot Running</h1>")

  print("Starting server on port 8080...")
  server = HTTPServer(('0.0.0.0', 8080), WebhookHandler)
  server.serve_forever()
