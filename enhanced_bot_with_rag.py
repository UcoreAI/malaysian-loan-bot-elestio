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
        self.whatsapp_token = os.getenv('WHATSAPP_TOKEN')
        
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
            print(f"❌ Database connection failed: {e}")
            
    def init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(host=self.redis_host, port=6379, decode_responses=True)
            self.redis_client.ping()
            print("✅ Redis connected")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
    
    def process_webhook(self, webhook_data):
        """Process incoming WhatsApp webhook"""
        try:
            message = webhook_data.get('messages', [{}])[0]
            phone_number = message.get('from', '')
            message_text = message.get('text', {}).get('body', '')
            
            if message_text and phone_number:
                # Save conversation to database
                self.save_conversation(phone_number, message_text)
                
                # Generate AI response
                response = self.generate_response(phone_number, message_text)
                
                # Send response via WhatsApp
                self.send_whatsapp_message(phone_number, response)
                
                return {"status": "processed", "response": response}
                
        except Exception as e:
            print(f"❌ Webhook processing error: {e}")
            return {"status": "error", "error": str(e)}
    
    def save_conversation(self, phone_number, message_text):
        """Save conversation to database"""
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (client_id, phone_number, message_text, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (self.client_id, phone_number, message_text, datetime.now()))
            self.db_conn.commit()
            cursor.close()
        except Exception as e:
            print(f"❌ Database save error: {e}")
    
    def generate_response(self, phone_number, message_text):
        """Generate AI response using OpenAI"""
        try:
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
            print(f"❌ AI response error: {e}")
            return "Sorry, I'm currently unavailable. Please try again later."
    
    def get_conversation_history(self, phone_number, limit=5):
        """Get recent conversation history from database"""
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
            print(f"❌ History retrieval error: {e}")
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
        
        return "\\n".join(prompt_parts)
    
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
                print("❌ WhatsApp token not configured")
                return False
                
            headers = {
                "Authorization": f"Bearer {self.whatsapp_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "to": phone_number,
                "body": message
            }
            
            response = requests.post(
                "https://gate.whapi.cloud/messages/text",
                headers=headers,
                json=data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ WhatsApp send error: {e}")
            return False

class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for WhatsApp webhooks"""
    
    def do_POST(self):
        """Handle POST requests (webhooks)"""
        try:
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
            
        except Exception as e:
            print(f"❌ Webhook handler error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests (health checks)"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health_data = {
                "status": "healthy",
                "service": "Malaysian Loan Bot",
                "client_id": bot.client_id,
                "timestamp": time.time()
            }
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Initialize bot
    bot = ElestioLoanBot()
    
    # Start HTTP server
    server_port = int(os.getenv('WEBHOOK_PORT', 8080))
    server = HTTPServer(('0.0.0.0', server_port), WebhookHandler)
    
    print(f"🚀 Malaysian Loan Bot server starting on port {server_port}")
    print(f"📱 Webhook endpoint: http://0.0.0.0:{server_port}/webhook")
    print(f"❤️  Health check: http://0.0.0.0:{server_port}/health")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user")
        server.shutdown()