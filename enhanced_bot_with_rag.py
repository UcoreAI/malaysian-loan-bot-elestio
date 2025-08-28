#!/usr/bin/env python3
  """
  Enhanced WhatsApp Bot with Database + RAG Integration
  Optimized for Elestio deployment
  """

  import json
  import requests
  import time
  import os
  from datetime import datetime
  from http.server import HTTPServer, BaseHTTPRequestHandler
  from typing import Dict, List, Optional
  from dotenv import load_dotenv
  import psycopg2
  import redis

  # Load environment variables
  load_dotenv()

  class ElestioLoanBot:
      """Streamlined Malaysian Loan Bot for Elestio deployment"""

      def __init__(self):
          # Configuration from environment
          self.client_id = os.getenv('CLIENT_ID', 'client_001')
          self.openai_api_key = os.getenv('OPENAI_API_KEY')
          self.whatsapp_token = os.getenv('MALAYSIAN_LOAN_WHATSAPP_TOKEN')

          # Database configuration
          self.db_config = {
              'host': os.getenv('POSTGRES_HOST', 'postgres'),
              'database': os.getenv('POSTGRES_DB', 'malaysian_loan_ai'),
              'user': os.getenv('POSTGRES_USER', 'postgres'),
              'password': os.getenv('POSTGRES_PASSWORD')
          }

          # Redis configuration
          self.redis_host = os.getenv('REDIS_HOST', 'redis')

          # Initialize connections
          self.init_database()
          self.init_redis()

          print(f"✅ Malaysian Loan Bot initialized for {self.client_id}")

      def init_database(self):
          """Initialize database connection"""
          try:
              self.db_conn = psycopg2.connect(**self.db_config)
              print("✅ Database connected")
          except Exception as e:
              print(f"⚠️ Database connection failed (will retry): {e}")
              self.db_conn = None

      def init_redis(self):
          """Initialize Redis connection"""
          try:
              self.redis_client = redis.Redis(host=self.redis_host, port=6379, decode_responses=True)
              self.redis_client.ping()
              print("✅ Redis connected")
          except Exception as e:
              print(f"⚠️ Redis connection failed (will retry): {e}")
              self.redis_client = None

      def process_webhook(self, webhook_data):
          """Process incoming WhatsApp webhook"""
          try:
              messages = webhook_data.get('messages', [])
              if not messages:
                  return {"status": "no_message"}

              message = messages[0]

              # Skip our own messages
              if message.get('from_me', False):
                  return {"status": "ignored"}

              phone_number = message.get('from', '')

              # Get text from message (Whapi format)
              message_text = message.get('body', '')
              if not message_text:
                  # Try getting from text field
                  text_data = message.get('text', {})
                  message_text = text_data.get('body', '')

              if message_text and phone_number:
                  print(f"📥 Received: '{message_text}' from {phone_number}")

                  # Save conversation to database
                  self.save_conversation(phone_number, message_text)

                  # Generate AI response
                  response = self.generate_response(phone_number, message_text)
                  print(f"🤖 Generated response: {response[:100]}...")

                  # Send response via WhatsApp
                  sent = self.send_whatsapp_message(phone_number, response)
                  print(f"📤 Message sent: {sent}")

                  return {"status": "processed", "response": response}
              else:
                  return {"status": "no_valid_message"}

          except Exception as e:
              print(f"❌ Webhook processing error: {e}")
              return {"status": "error", "error": str(e)}

      def save_conversation(self, phone_number, message_text):
          """Save conversation to database"""
          if not self.db_conn:
              self.init_database()

          if not self.db_conn:
              print("⚠️ Database not available, skipping save")
              return

          try:
              cursor = self.db_conn.cursor()
              cursor.execute("""
                  INSERT INTO conversations (client_id, phone_number, message_text, timestamp)
                  VALUES (%s, %s, %s, %s)
              """, (self.client_id, phone_number, message_text, datetime.now()))
              self.db_conn.commit()
              cursor.close()
          except Exception as e:
              print(f"⚠️ Database save error: {e}")
              self.db_conn = None

      def generate_response(self, phone_number, message_text):
          """Generate AI response using OpenAI"""
          try:
              if not self.openai_api_key:
                  return "Hello! I'm your Malaysian Loan consultant. I'm currently being configured. Please try
  again soon!"

              # Get conversation history
              history = self.get_conversation_history(phone_number)

              # Build prompt
              prompt = self.build_prompt(history, message_text)

              # Call OpenAI API
              headers = {
                  "Authorization": f"Bearer {self.openai_api_key}",
                  "Content-Type": "application/json"
              }

              data = {
                  "model": "gpt-4o-mini",
                  "messages": [
                      {"role": "system", "content": self.system_prompt()},
                      {"role": "user", "content": prompt}
                  ],
                  "max_tokens": 500,
                  "temperature": 0.7
              }

              response = requests.post(
                  "https://api.openai.com/v1/chat/completions",
                  headers=headers,
                  json=data,
                  timeout=10
              )

              if response.status_code == 200:
                  result = response.json()
                  return result['choices'][0]['message']['content']
              else:
                  return "Sorry, I'm experiencing technical difficulties. Please try again."

          except Exception as e:
              print(f"⚠️ AI response error: {e}")
              return "Hello! I'm your Malaysian Loan consultant. I'm currently being configured. Please try again
  soon!"

      def get_conversation_history(self, phone_number, limit=5):
          """Get recent conversation history from database"""
          if not self.db_conn:
              return []

          try:
              cursor = self.db_conn.cursor()
              cursor.execute("""
                  SELECT message_text, response_text, timestamp
                  FROM conversations
                  WHERE phone_number = %s AND client_id = %s
                  ORDER BY timestamp DESC
                  LIMIT %s
              """, (phone_number, self.client_id, limit))

              history = cursor.fetchall()
              cursor.close()
              return history[::-1]  # Reverse to get chronological order

          except Exception as e:
              print(f"⚠️ History retrieval error: {e}")
              self.db_conn = None
              return []

      def build_prompt(self, history, current_message):
          """Build conversation prompt with history"""
          prompt_parts = []

          if history:
              prompt_parts.append("Recent conversation history:")
              for msg_text, response_text, timestamp in history:
                  prompt_parts.append(f"Customer: {msg_text}")
                  if response_text:
                      prompt_parts.append(f"Assistant: {response_text}")

          prompt_parts.append(f"Current message: {current_message}")
          prompt_parts.append("Please respond as a Malaysian loan consultant.")

          return "\n".join(prompt_parts)

      def system_prompt(self):
          """System prompt for Malaysian loan consultant"""
          return """You are Stephy, an expert Malaysian loan consultant AI assistant.

  EXPERTISE:
  - Personal loans, housing loans, car loans
  - Malaysian banking regulations and requirements
  - CTOS credit reports and scoring
  - Loan eligibility assessment
  - Document requirements

  PERSONALITY:
  - Professional yet friendly
  - Patient and helpful
  - Uses Malaysian context (RM, Malaysian banks)
  - Multilingual (English, some Bahasa Malaysia)

  IMPORTANT RULES:
  - Never guarantee loan approvals
  - Always mention document verification needed
  - Refer complex cases to human agents
  - Keep responses concise and actionable

  Respond professionally and helpfully to loan-related inquiries."""

      def send_whatsapp_message(self, phone_number, message):
          """Send message via WhatsApp API"""
          try:
              if not self.whatsapp_token:
                  print("⚠️ WhatsApp token not configured")
                  return False

              headers = {
                  "Authorization": f"Bearer {self.whatsapp_token}",
                  "Content-Type": "application/json"
              }

              # Add @s.whatsapp.net to phone number
              if not phone_number.endswith('@s.whatsapp.net'):
                  phone_number = f"{phone_number}@s.whatsapp.net"

              data = {
                  "to": phone_number,
                  "body": message,
                  "typing_time": 3
              }

              print(f"📱 Sending to Whapi: {phone_number}")

              response = requests.post(
                  "https://gate.whapi.cloud/messages/text",
                  headers=headers,
                  json=data,
                  timeout=10
              )

              print(f"📡 Whapi response: {response.status_code} - {response.text[:200]}")

              return response.status_code == 200 or response.status_code == 201

          except Exception as e:
              print(f"⚠️ WhatsApp send error: {e}")
              return False

  class WebhookHandler(BaseHTTPRequestHandler):
      """HTTP handler for WhatsApp webhooks"""

      def do_POST(self):
          """Handle POST requests (webhooks)"""
          try:
              # Handle webhook path
              if self.path == '/webhook' or self.path == '/client/001/webhook':
                  content_length = int(self.headers['Content-Length'])
                  post_data = self.rfile.read(content_length)
                  webhook_data = json.loads(post_data.decode('utf-8'))

                  # Process webhook
                  result = bot.process_webhook(webhook_data)

                  # Send response
                  self.send_response(200)
                  self.send_header('Content-type', 'application/json')
                  self.end_headers()
                  self.wfile.write(json.dumps(result).encode())
              else:
                  self.send_response(404)
                  self.send_header('Content-type', 'application/json')
                  self.end_headers()
                  self.wfile.write(json.dumps({"error": "Not found"}).encode())

          except Exception as e:
              print(f"❌ Webhook handler error: {e}")
              self.send_response(500)
              self.send_header('Content-type', 'application/json')
              self.end_headers()
              self.wfile.write(json.dumps({"error": str(e)}).encode())

      def do_GET(self):
          """Handle GET requests"""
          try:
              if self.path == '/health':
                  # Health check endpoint
                  health_data = {
                      "status": "healthy",
                      "service": "Malaysian Loan Bot",
                      "client_id": bot.client_id,
                      "timestamp": time.time(),
                      "database": "connected" if bot.db_conn else "disconnected",
                      "redis": "connected" if bot.redis_client else "disconnected",
                      "openai": "configured" if bot.openai_api_key else "not configured",
                      "whatsapp": "configured" if bot.whatsapp_token else "not configured"
                  }

                  self.send_response(200)
                  self.send_header('Content-type', 'application/json')
                  self.end_headers()
                  self.wfile.write(json.dumps(health_data, indent=2).encode())

              elif self.path == '/' or self.path == '':
                  # Root path - show status page
                  html_content = f"""
                  <!DOCTYPE html>
                  <html>
                  <head>
                      <title>Malaysian Loan Bot - Status</title>
                      <style>
                          body {{
                              font-family: Arial, sans-serif;
                              max-width: 800px;
                              margin: 50px auto;
                              padding: 20px;
                              background: #f5f5f5;
                          }}
                          .container {{
                              background: white;
                              padding: 30px;
                              border-radius: 10px;
                              box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                          }}
                          h1 {{
                              color: #2c3e50;
                              border-bottom: 2px solid #3498db;
                              padding-bottom: 10px;
                          }}
                          .status {{
                              background: #2ecc71;
                              color: white;
                              padding: 10px 20px;
                              border-radius: 5px;
                              display: inline-block;
                              margin: 20px 0;
                          }}
                          .endpoints {{
                              background: #ecf0f1;
                              padding: 20px;
                              border-radius: 5px;
                              margin: 20px 0;
                          }}
                          .endpoint {{
                              margin: 10px 0;
                              padding: 10px;
                              background: white;
                              border-left: 4px solid #3498db;
                          }}
                          code {{
                              background: #f4f4f4;
                              padding: 2px 6px;
                              border-radius: 3px;
                              font-family: monospace;
                          }}
                          .config {{
                              background: #fff3cd;
                              padding: 15px;
                              border-left: 4px solid #ffc107;
                              margin: 20px 0;
                          }}
                      </style>
                  </head>
                  <body>
                      <div class="container">
                          <h1>🏦 Malaysian Loan Bot</h1>
                          <div class="status">✅ Service Running</div>

                          <h2>API Endpoints</h2>
                          <div class="endpoints">
                              <div class="endpoint">
                                  <strong>Health Check:</strong><br>
                                  <code>GET /health</code><br>
                                  Returns service health status
                              </div>
                              <div class="endpoint">
                                  <strong>WhatsApp Webhook:</strong><br>
                                  <code>POST /client/001/webhook</code><br>
                                  Receives WhatsApp messages
                              </div>
                          </div>

                          <h2>Configuration Status</h2>
                          <div class="config">
                              <ul>
                                  <li>Client ID: <code>{bot.client_id}</code></li>
                                  <li>Database: {'✅ Connected' if bot.db_conn else '⚠️ Disconnected'}</li>
                                  <li>Redis: {'✅ Connected' if bot.redis_client else '⚠️ Disconnected'}</li>
                                  <li>OpenAI: {'✅ Configured' if bot.openai_api_key else '⚠️ Not Configured'}</li>
                                  <li>WhatsApp: {'✅ Configured' if bot.whatsapp_token else '⚠️ Not
  Configured'}</li>
                              </ul>
                          </div>

                          <p style="margin-top: 30px; color: #7f8c8d;">
                              Powered by UcoreAI • Deployed on Elestio
                          </p>
                      </div>
                  </body>
                  </html>
                  """

                  self.send_response(200)
                  self.send_header('Content-type', 'text/html')
                  self.end_headers()
                  self.wfile.write(html_content.encode())

              else:
                  # Unknown path
                  self.send_response(404)
                  self.send_header('Content-type', 'application/json')
                  self.end_headers()
                  self.wfile.write(json.dumps({
                      "error": "Not found",
                      "available_endpoints": ["/", "/health", "/client/001/webhook"]
                  }).encode())

          except Exception as e:
              print(f"❌ GET handler error: {e}")
              self.send_response(500)
              self.send_header('Content-type', 'application/json')
              self.end_headers()
              self.wfile.write(json.dumps({"error": str(e)}).encode())

      def log_message(self, format, *args):
          """Override to reduce log verbosity"""
          # Log all requests for debugging
          print(f"{self.address_string()} - {format % args}")

  if __name__ == "__main__":
      print("🚀 Starting Malaysian Loan Bot...")

      # Initialize bot
      try:
          bot = ElestioLoanBot()
      except Exception as e:
          print(f"❌ Failed to initialize bot: {e}")
          sys.exit(1)

      # Start HTTP server
      server_port = int(os.getenv('WEBHOOK_PORT', 8080))

      try:
          server = HTTPServer(('0.0.0.0', server_port), WebhookHandler)
          print(f"🚀 Malaysian Loan Bot server starting on port {server_port}")
          print(f"📱 Webhook endpoint: http://0.0.0.0:{server_port}/client/001/webhook")
          print(f"❤️  Health check: http://0.0.0.0:{server_port}/health")
          print(f"🏠 Status page: http://0.0.0.0:{server_port}/")
          print("✅ Server ready!")

          server.serve_forever()
      except Exception as e:
          print(f"❌ Server failed to start: {e}")
          sys.exit(1)
      except KeyboardInterrupt:
          print("\n🛑 Server stopped by user")
          server.shutdown()
