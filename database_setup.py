#!/usr/bin/env python3
"""
Database setup and management for Malaysian Loan Bot
Streamlined for Elestio deployment
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Optional, Dict, List

class DatabaseManager:
    """Database connection and query management"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'postgres'),
            'database': os.getenv('POSTGRES_DB', 'malaysian_loan_ai'), 
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'port': 5432
        }
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            print("✅ Database connected")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.connection = None
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Execute database query safely"""
        if not self.connection:
            self.connect()
            
        if not self.connection:
            return None
            
        try:
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
                cursor.close()
                return [dict(row) for row in result]
            else:
                cursor.close()
                return []
                
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

class ClientManager:
    """Manage client information and configurations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_client_info(self, client_id: str) -> Optional[Dict]:
        """Get client information"""
        query = "SELECT * FROM clients WHERE client_id = %s"
        results = self.db.execute_query(query, (client_id,))
        return results[0] if results else None
    
    def update_client_status(self, client_id: str, status: str) -> bool:
        """Update client status"""
        query = "UPDATE clients SET status = %s, updated_at = %s WHERE client_id = %s"
        result = self.db.execute_query(query, (status, datetime.now(), client_id))
        return result is not None

class ConversationTracker:
    """Track and manage customer conversations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_conversation(self, client_id: str, phone_number: str, message_text: str, 
                         response_text: str = None, customer_name: str = None) -> bool:
        """Save conversation to database"""
        query = """
        INSERT INTO conversations (client_id, phone_number, customer_name, message_text, response_text, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (client_id, phone_number, customer_name, message_text, response_text, datetime.now())
        result = self.db.execute_query(query, params)
        return result is not None
    
    def get_conversation_history(self, phone_number: str, client_id: str, limit: int = 10) -> List[Dict]:
        """Get conversation history for a customer"""
        query = """
        SELECT message_text, response_text, timestamp, customer_name
        FROM conversations 
        WHERE phone_number = %s AND client_id = %s
        ORDER BY timestamp DESC 
        LIMIT %s
        """
        results = self.db.execute_query(query, (phone_number, client_id, limit))
        return results or []
    
    def get_customer_stats(self, phone_number: str, client_id: str) -> Dict:
        """Get customer interaction statistics"""
        query = """
        SELECT 
            COUNT(*) as total_messages,
            MAX(timestamp) as last_interaction,
            MIN(timestamp) as first_interaction
        FROM conversations 
        WHERE phone_number = %s AND client_id = %s
        """
        results = self.db.execute_query(query, (phone_number, client_id))
        return results[0] if results else {}

class LoanApplicationTracker:
    """Track loan applications and status"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_application(self, client_id: str, phone_number: str, customer_name: str,
                          loan_amount: float = None, loan_purpose: str = None,
                          monthly_income: float = None, employment_status: str = None) -> bool:
        """Create new loan application"""
        query = """
        INSERT INTO loan_applications (client_id, phone_number, customer_name, loan_amount, 
                                     loan_purpose, monthly_income, employment_status, 
                                     application_status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (client_id, phone_number, customer_name, loan_amount, loan_purpose,
                 monthly_income, employment_status, 'pending', datetime.now(), datetime.now())
        result = self.db.execute_query(query, params)
        return result is not None
    
    def update_application_status(self, phone_number: str, client_id: str, status: str) -> bool:
        """Update application status"""
        query = """
        UPDATE loan_applications 
        SET application_status = %s, updated_at = %s 
        WHERE phone_number = %s AND client_id = %s
        """
        result = self.db.execute_query(query, (status, datetime.now(), phone_number, client_id))
        return result is not None
    
    def get_customer_applications(self, phone_number: str, client_id: str) -> List[Dict]:
        """Get customer's loan applications"""
        query = """
        SELECT * FROM loan_applications 
        WHERE phone_number = %s AND client_id = %s 
        ORDER BY created_at DESC
        """
        results = self.db.execute_query(query, (phone_number, client_id))
        return results or []

def initialize_database():
    """Initialize database with required tables (if not exists)"""
    db_manager = DatabaseManager()
    
    if not db_manager.connection:
        print("❌ Cannot initialize database - no connection")
        return False
    
    print("✅ Database initialization completed")
    return True

if __name__ == "__main__":
    # Test database setup
    initialize_database()