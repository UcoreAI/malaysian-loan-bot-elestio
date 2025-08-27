#!/usr/bin/env python3
"""
Simple RAG System for Malaysian Loan Bot
Streamlined for Elestio deployment
"""

import os
import json
import numpy as np
from typing import List, Dict, Optional
import openai
from sentence_transformers import SentenceTransformer

class SimpleLoanRAG:
    """Simple RAG system for loan consultation knowledge"""
    
    def __init__(self, knowledge_base_path: str = "/app/knowledge_base"):
        self.knowledge_base_path = knowledge_base_path
        self.documents = []
        self.embeddings = []
        self.embedding_model = None
        
        # Initialize embedding model
        self.init_embedding_model()
        
        # Load knowledge base
        self.load_knowledge_base()
        
    def init_embedding_model(self):
        """Initialize sentence transformer model"""
        try:
            # Use lightweight model for 2GB constraint
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ RAG embedding model loaded")
        except Exception as e:
            print(f"❌ RAG model loading error: {e}")
    
    def load_knowledge_base(self):
        """Load existing knowledge base or create default"""
        try:
            if os.path.exists(self.knowledge_base_path):
                self.load_documents_from_directory()
            else:
                self.create_default_knowledge()
                
            print(f"✅ Knowledge base loaded: {len(self.documents)} documents")
            
        except Exception as e:
            print(f"❌ Knowledge base loading error: {e}")
    
    def create_default_knowledge(self):
        """Create default Malaysian loan knowledge"""
        default_docs = [
            {
                "title": "Personal Loan Eligibility",
                "content": "Malaysian personal loan eligibility requires: minimum age 18-21, maximum age 55-65, minimum monthly income RM2,000-3,000, employment period minimum 6 months, CTOS score above 600, debt service ratio below 60%."
            },
            {
                "title": "Housing Loan Requirements", 
                "content": "Malaysian housing loan requires: minimum income RM3,000, down payment 10%-20%, maximum loan tenure 35 years, debt service ratio below 70%, property valuation report, legal fees 0.25%-1%."
            },
            {
                "title": "Car Loan Guidelines",
                "content": "Malaysian car loan guidelines: maximum 90% financing, tenure up to 9 years, minimum income RM2,500, age limit 65 years, comprehensive insurance required, road tax and registration fees."
            },
            {
                "title": "CTOS Credit Report",
                "content": "CTOS credit report shows payment history, outstanding debts, legal cases, directorship information. Score ranges: 300-850, above 700 excellent, 650-699 good, 600-649 fair, below 600 poor. Cost RM25 per report."
            },
            {
                "title": "Required Documents",
                "content": "Standard loan documents: IC copy front/back, latest 3 months salary slip, latest 6 months bank statement, EPF statement, employment letter, CTOS report. Additional for housing: property documents, valuation report."
            }
        ]
        
        self.documents = default_docs
        self.generate_embeddings()
    
    def load_documents_from_directory(self):
        """Load documents from knowledge base directory"""
        self.documents = []
        
        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.knowledge_base_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        doc = json.load(f)
                        self.documents.append(doc)
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        
        if self.documents:
            self.generate_embeddings()
    
    def generate_embeddings(self):
        """Generate embeddings for all documents"""
        if not self.embedding_model or not self.documents:
            return
            
        try:
            # Combine title and content for embedding
            texts = [f"{doc['title']}: {doc['content']}" for doc in self.documents]
            
            # Generate embeddings
            self.embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            print(f"✅ Generated embeddings for {len(texts)} documents")
            
        except Exception as e:
            print(f"❌ Embedding generation error: {e}")
    
    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search knowledge base using semantic similarity"""
        if not self.embedding_model or not self.embeddings or not query.strip():
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            
            # Calculate similarities
            similarities = np.dot(self.embeddings, query_embedding.T).flatten()
            
            # Get top matches
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # Minimum similarity threshold
                    results.append({
                        "document": self.documents[idx],
                        "similarity": float(similarities[idx])
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Knowledge search error: {e}")
            return []
    
    def get_relevant_context(self, query: str) -> str:
        """Get relevant context for a query"""
        try:
            results = self.search_knowledge(query, top_k=2)
            
            if not results:
                return "No specific information found in knowledge base."
            
            context_parts = []
            for result in results:
                doc = result["document"]
                context_parts.append(f"{doc['title']}: {doc['content']}")
            
            return "\\n\\n".join(context_parts)
            
        except Exception as e:
            print(f"❌ Context retrieval error: {e}")
            return "Error retrieving relevant information."
    
    def enhance_response_with_knowledge(self, query: str, base_response: str) -> str:
        """Enhance response with relevant knowledge"""
        try:
            relevant_context = self.get_relevant_context(query)
            
            if "No specific information" in relevant_context:
                return base_response
            
            # Simple enhancement - add relevant info if not already covered
            enhanced_response = base_response
            
            # Add knowledge if response seems incomplete
            if len(base_response.split()) < 50:  # Short response
                enhanced_response += f"\\n\\nAdditional information:\\n{relevant_context}"
            
            return enhanced_response
            
        except Exception as e:
            print(f"❌ Response enhancement error: {e}")
            return base_response

class LoanRAGPresets:
    """Preset knowledge for Malaysian loan consultation"""
    
    @staticmethod
    def get_malaysian_loan_knowledge() -> List[Dict]:
        """Get comprehensive Malaysian loan knowledge"""
        return [
            {
                "title": "Bank Negara Malaysia Guidelines",
                "content": "BNM sets maximum debt service ratio at 60% for personal loans, 70% for housing loans. Cooling-off period 5 days for personal loans. Banks must conduct affordability assessment."
            },
            {
                "title": "Popular Malaysian Banks",
                "content": "Major banks: Maybank, CIMB, Public Bank, RHB, Hong Leong Bank, AmBank, Bank Islam, Bank Rakyat. Each has different eligibility criteria and interest rates."
            },
            {
                "title": "Loan Interest Rates",
                "content": "Current Malaysian rates (approximate): Personal loans 6-18%, Housing loans 3.5-4.5%, Car loans 2.5-4%. Rates vary by bank, loan amount, and credit score."
            },
            {
                "title": "Government Loan Schemes",
                "content": "PR1MA housing scheme, My First Home Scheme, Fund for Food scheme. Special rates and terms for first-time buyers and specific groups."
            }
        ]

# Initialize global RAG system
rag_system = SimpleLoanRAG()

if __name__ == "__main__":
    # Test the RAG system
    test_query = "What are the requirements for a personal loan?"
    context = rag_system.get_relevant_context(test_query)
    print(f"Query: {test_query}")
    print(f"Context: {context}")