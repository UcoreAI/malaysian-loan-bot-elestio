#!/usr/bin/env python3
"""
Simple health check endpoint for Malaysian Loan Bot
"""

import requests
import sys
import os
from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Basic health check endpoint"""
    try:
        # Basic system checks
        checks = {
            "status": "healthy",
            "service": "Malaysian Loan Bot",
            "timestamp": time.time(),
            "client_id": os.getenv('CLIENT_ID', 'client_001'),
            "memory_limit": os.getenv('PYTHON_MEMORY_LIMIT', '1000m'),
            "rag_enabled": os.getenv('RAG_ENABLED', 'true').lower() == 'true'
        }
        
        # Check database connectivity if available
        try:
            import psycopg2
            conn_string = f"host={os.getenv('POSTGRES_HOST', 'localhost')} port=5432 dbname={os.getenv('POSTGRES_DB', 'malaysian_loan_ai')} user={os.getenv('POSTGRES_USER', 'postgres')} password={os.getenv('POSTGRES_PASSWORD', '')}"
            conn = psycopg2.connect(conn_string)
            conn.close()
            checks["database"] = "connected"
        except:
            checks["database"] = "disconnected"
            
        # Check Redis if available
        try:
            import redis
            r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, decode_responses=True)
            r.ping()
            checks["redis"] = "connected"
        except:
            checks["redis"] = "disconnected"
            
        return checks, 200
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }, 500

if __name__ == "__main__":
    # Run health check
    try:
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            sys.exit(0)
        else:
            print("❌ Health check failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Health check error: {e}")
        sys.exit(1)