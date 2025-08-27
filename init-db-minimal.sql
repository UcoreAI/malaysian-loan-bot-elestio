-- Initialize minimal database for Malaysian Loan Bot (Single Client)
-- Optimized for 2GB VPS deployment

-- Database will be created automatically by Docker compose POSTGRES_DB
-- We're already connected to malaysian_loan_ai database

-- Create clients table for Malaysian Loan Bot
CREATE TABLE IF NOT EXISTS clients (
    client_id VARCHAR(50) PRIMARY KEY,
    client_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create conversations table for chat history
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(50) REFERENCES clients(client_id),
    phone_number VARCHAR(20) NOT NULL,
    customer_name VARCHAR(100),
    message_text TEXT NOT NULL,
    response_text TEXT,
    message_type VARCHAR(20) DEFAULT 'text',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER,
    rag_used BOOLEAN DEFAULT false,
    escalated BOOLEAN DEFAULT false
);

-- Create loan_applications table for tracking loan requests
CREATE TABLE IF NOT EXISTS loan_applications (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(50) REFERENCES clients(client_id),
    phone_number VARCHAR(20) NOT NULL,
    customer_name VARCHAR(100),
    loan_amount DECIMAL(12,2),
    loan_purpose VARCHAR(200),
    monthly_income DECIMAL(10,2),
    employment_status VARCHAR(50),
    application_status VARCHAR(30) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create customer_documents table for document tracking
CREATE TABLE IF NOT EXISTS customer_documents (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_status VARCHAR(30) DEFAULT 'pending',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    notes TEXT
);

-- Create system_metrics table for basic monitoring
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default Malaysian Loan client
INSERT INTO clients (client_id, client_name, status) VALUES 
('client_001', 'Malaysian Loan Consultant', 'active')
ON CONFLICT (client_id) DO NOTHING;

-- Create indexes for better performance (minimal for 2GB VPS)
CREATE INDEX IF NOT EXISTS idx_conversations_phone ON conversations(phone_number);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX IF NOT EXISTS idx_loan_applications_phone ON loan_applications(phone_number);
CREATE INDEX IF NOT EXISTS idx_customer_documents_phone ON customer_documents(phone_number);

-- Create a function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_clients_updated_at 
    BEFORE UPDATE ON clients 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_loan_applications_updated_at 
    BEFORE UPDATE ON loan_applications 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Insert initial system metrics
INSERT INTO system_metrics (metric_name, metric_value) VALUES
('total_conversations', 0),
('total_applications', 0),
('system_uptime_hours', 0)
ON CONFLICT DO NOTHING;

-- Display initialization success
SELECT 'Malaysian Loan AI Database initialized successfully!' as status;