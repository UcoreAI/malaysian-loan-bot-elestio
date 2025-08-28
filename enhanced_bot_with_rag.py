#!/usr/bin/env python3
import json
import os
  from http.server import HTTPServer, BaseHTTPRequestHandler

  class DiagnosticBot:
      def __init__(self):
          print("DIAGNOSTIC MODE - Checking environment...")
          self.openai_key = os.getenv('OPENAI_API_KEY')
          self.whatsapp_token = os.getenv('MALAYSIAN_LOAN_WHATSAPP_TOKEN')
          self.whatsapp_token_alt = os.getenv('WHATSAPP_TOKEN')
          print(f"OPENAI_API_KEY: {'SET' if self.openai_key else 'MISSING'}")
          print(f"MALAYSIAN_LOAN_WHATSAPP_TOKEN: {'SET' if self.whatsapp_token else 'MISSING'}")
          print(f"WHATSAPP_TOKEN: {'SET' if self.whatsapp_token_alt else 'MISSING'}")
          if self.whatsapp_token:
              print(f"Token starts with: {self.whatsapp_token[:10]}...")
          elif self.whatsapp_token_alt:
              print(f"Alt token starts with: {self.whatsapp_token_alt[:10]}...")
          else:
              print("NO WHATSAPP TOKEN FOUND!")

      def process_webhook(self, webhook_data):
          print("WEBHOOK RECEIVED:")
          print(json.dumps(webhook_data, indent=2))
          try:
              messages = webhook_data.get('messages', [])
              if not messages:
                  print("No messages in webhook")
                  return {"status": "no_message"}
              message = messages[0]
              if message.get('from_me', False):
                  print("Ignoring own message")
                  return {"status": "ignored"}
              phone_number = message.get('from', '')
              message_text = message.get('text', {}).get('body', '')
              print(f"Phone: {phone_number}")
              print(f"Message: {message_text}")
              if not self.whatsapp_token and not self.whatsapp_token_alt:
                  print("CANNOT SEND - NO WHATSAPP TOKEN!")
                  return {"status": "no_token"}
              print("Would send response but skipping for diagnostic")
              return {"status": "diagnostic_complete"}
          except Exception as e:
              print(f"ERROR: {e}")
              return {"status": "error", "error": str(e)}

  class WebhookHandler(BaseHTTPRequestHandler):
      def do_POST(self):
          print(f"POST request to: {self.path}")
          if self.path == '/webhook' or self.path == '/client/001/webhook':
              content_length = int(self.headers['Content-Length'])
              post_data = self.rfile.read(content_length)
              webhook_data = json.loads(post_data.decode('utf-8'))
              result = bot.process_webhook(webhook_data)
              self.send_response(200)
              self.send_header('Content-type', 'application/json')
              self.end_headers()
              self.wfile.write(json.dumps(result).encode())
          else:
              print(f"Unknown path: {self.path}")
              self.send_response(404)
              self.end_headers()

      def do_GET(self):
          print(f"GET request to: {self.path}")
          if self.path == '/health':
              health = {
                  "status": "diagnostic",
                  "openai": bool(bot.openai_key),
                  "whatsapp_token": bool(bot.whatsapp_token),
                  "whatsapp_token_alt": bool(bot.whatsapp_token_alt)
              }
              self.send_response(200)
              self.send_header('Content-type', 'application/json')
              self.end_headers()
              self.wfile.write(json.dumps(health, indent=2).encode())
          else:
              self.send_response(200)
              self.send_header('Content-type', 'text/html')
              self.end_headers()
              self.wfile.write(b"<h1>DIAGNOSTIC MODE</h1><p>Check logs for details</p>")

      def log_message(self, format, *args):
          print(f"{self.address_string()} - {format % args}")

  if __name__ == "__main__":
      print("STARTING DIAGNOSTIC BOT...")
      print("=" * 50)
      bot = DiagnosticBot()
      print("=" * 50)
      server_port = int(os.getenv('WEBHOOK_PORT', 8080))
      server = HTTPServer(('0.0.0.0', server_port), WebhookHandler)
      print(f"Diagnostic server ready on port {server_port}")
      print("Send a WhatsApp message now...")
      server.serve_forever()
