#!/usr/bin/env python3
"""
Simplified RAG System Stub for Malaysian Loan Bot
(Minimal implementation to avoid dependency issues)
"""

class SimpleLoanRAG:
    """Simplified RAG system without heavy dependencies"""
    
    def __init__(self, knowledge_base_path: str = "/app/knowledge_base"):
        self.knowledge_base_path = knowledge_base_path
        self.documents = self.get_default_knowledge()
        print("✅ Simple knowledge base initialized")
    
    def get_default_knowledge(self):
        """Return default Malaysian loan knowledge"""
        return [
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
    
    def search_knowledge(self, query: str, top_k: int = 3):
        """Simple keyword search without embeddings"""
        query_lower = query.lower()
        results = []
        
        for doc in self.documents:
            # Simple keyword matching
            content_lower = (doc['title'] + ' ' + doc['content']).lower()
            if any(word in content_lower for word in query_lower.split()):
                results.append({
                    "document": doc,
                    "similarity": 0.5  # Fixed similarity score
                })
        
        return results[:top_k]
    
    def get_relevant_context(self, query: str) -> str:
        """Get relevant context for a query"""
        results = self.search_knowledge(query, top_k=2)
        
        if not results:
            return "No specific information found in knowledge base."
        
        context_parts = []
        for result in results:
            doc = result["document"]
            context_parts.append(f"{doc['title']}: {doc['content']}")
        
        return "\n\n".join(context_parts)
    
    def enhance_response_with_knowledge(self, query: str, base_response: str) -> str:
        """Enhance response with relevant knowledge"""
        relevant_context = self.get_relevant_context(query)
        
        if "No specific information" in relevant_context:
            return base_response
        
        # Simple enhancement
        enhanced_response = base_response
        if len(base_response.split()) < 50:
            enhanced_response += f"\n\nAdditional information:\n{relevant_context}"
        
        return enhanced_response

class LoanRAGPresets:
    """Preset knowledge for Malaysian loan consultation"""
    
    @staticmethod
    def get_malaysian_loan_knowledge():
        """Get comprehensive Malaysian loan knowledge"""
        return [
            {
                "title": "Bank Negara Malaysia Guidelines",
                "content": "BNM sets maximum debt service ratio at 60% for personal loans, 70% for housing loans. Cooling-off period 5 days for personal loans."
            },
            {
                "title": "Popular Malaysian Banks",
                "content": "Major banks: Maybank, CIMB, Public Bank, RHB, Hong Leong Bank, AmBank, Bank Islam, Bank Rakyat."
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