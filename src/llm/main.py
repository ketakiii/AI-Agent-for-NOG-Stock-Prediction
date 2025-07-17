from src.llm.query_classifier import QueryClassifier
from src.llm.rag_retrieval import ChromaDBRetriever
from src.llm.llm_inference import generate_answers
import os
from typing import List, Dict

class NOGAnalysisSystem:
    """
    Main system that integrates RAG, query classification, and LLM inference
    for comprehensive NOG stock analysis.
    """
    
    def __init__(self, collection_name: str = "nog_corpus"):
        """
        Initialize the NOG analysis system.
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.query_classifier = QueryClassifier()
        self.retriever = ChromaDBRetriever(collection_name=collection_name)
        print("[INFO] NOG Analysis System initialized")
    
    def analyze_query(self, query: str, top_k: int = 5) -> Dict:
        """
        Analyze a user query and provide comprehensive response.
        
        Args:
            query: User's question about NOG
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary containing analysis results
        """
        # Classify the query intent
        intent = self.query_classifier.classify_query(query)
        print(f"[INFO] Query classified as: {intent}")
        
        # Retrieve relevant documents
        relevant_docs = self.retriever.search(query, top_k=top_k)
        
        if not relevant_docs:
            return {
                "query": query,
                "intent": intent,
                "answer": "I don't have enough relevant information to answer this question about NOG.",
                "sources": [],
                "confidence": "low"
            }
        
        # Extract text content for LLM
        context_texts = [doc['text'] for doc in relevant_docs]
        
        # Generate answer using LLM
        try:
            answer = generate_answers(query, context_texts)
        except Exception as e:
            print(f"[ERROR] LLM inference failed: {e}")
            answer = "I encountered an error while generating the answer. Please try again."
        
        # Prepare response
        response = {
            "query": query,
            "intent": intent,
            "answer": answer,
            "sources": [
                {
                    "text": doc['text'][:200] + "...",
                    "metadata": doc['metadata'],
                    "relevance_score": 1 - (doc['distance'] if doc['distance'] else 0)
                }
                for doc in relevant_docs
            ],
            "confidence": "high" if len(relevant_docs) >= 3 else "medium"
        }
        
        return response
    
    def get_system_stats(self) -> Dict:
        """
        Get system statistics and health check.
        
        Returns:
            Dictionary with system statistics
        """
        collection_stats = self.retriever.get_collection_stats()
        
        return {
            "system": "NOG Analysis System",
            "status": "operational",
            "collection_stats": collection_stats,
            "components": {
                "query_classifier": "active",
                "rag_retriever": "active",
                "llm_inference": "active"
            }
        }

def main():
    """
    Main entry point for the NOG analysis system.
    """
    # Initialize the system
    system = NOGAnalysisSystem()
    
    # Example usage
    print("\n=== NOG Analysis System ===")
    print("Ask questions about Northern Oil & Gas (NOG)")
    print("Type 'quit' to exit")
    print("Type 'stats' to see system statistics")
    print("=" * 30)
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if query.lower() == 'quit':
                print("Goodbye!")
                break
            elif query.lower() == 'stats':
                stats = system.get_system_stats()
                print(f"\nSystem Statistics:")
                print(f"  - Total documents: {stats['collection_stats']['total_documents']}")
                print(f"  - Collection: {stats['collection_stats']['collection_name']}")
                print(f"  - Status: {stats['status']}")
                continue
            elif not query:
                continue
            
            # Analyze the query
            result = system.analyze_query(query)
            
            # Display results
            print(f"\n📊 Intent: {result['intent']}")
            print(f"🤖 Answer: {result['answer']}")
            print(f"📈 Confidence: {result['confidence']}")
            
            if result['sources']:
                print(f"\n📚 Sources ({len(result['sources'])}):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source['text']}")
                    if source['metadata']:
                        print(f"     Metadata: {source['metadata']}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {e}")

if __name__ == "__main__":
    main()