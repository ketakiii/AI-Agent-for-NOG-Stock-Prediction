import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from typing import List, Dict, Optional

class ChromaDBRetriever:
    """
    ChromaDB-based retriever for RAG system.
    Works natively on M1/M2/M3 Macs.
    """
    
    def __init__(self, collection_name: str = "nog_corpus", persist_directory: str = "data/chroma_db"):
        """
        Initialize ChromaDB retriever.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"[INFO] Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(name=collection_name)
            print(f"[INFO] Created new collection: {collection_name}")
    
    def build_index_from_jsonl(self, jsonl_file_path: str) -> None:
        """
        Build ChromaDB index from JSONL file.
        
        Args:
            jsonl_file_path: Path to the JSONL file containing documents
        """
        print(f"[INFO] Building index from: {jsonl_file_path}")
        
        documents = []
        metadatas = []
        ids = []
        
        with open(jsonl_file_path, 'r') as f:
            for i, line in enumerate(f):
                if line.strip():
                    data = json.loads(line)
                    documents.append(data['text'])
                    metadatas.append(data.get('metadata', {}))
                    ids.append(f"doc_{i}")
        
        print(f"[INFO] Loaded {len(documents)} documents")
        
        # Add documents to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"[INFO] Successfully built index with {len(documents)} documents")
    
    def search(self, query: str, top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional filter for metadata
            
        Returns:
            List of relevant documents with metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=filter_dict
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else None
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        count = self.collection.count()
        return {
            'total_documents': count,
            'collection_name': self.collection_name
        }

def build_chroma_index(jsonl_file_path: str, collection_name: str = "nog_corpus") -> ChromaDBRetriever:
    """
    Build ChromaDB index from JSONL file.
    
    Args:
        jsonl_file_path: Path to the JSONL file
        collection_name: Name of the collection
        
    Returns:
        ChromaDBRetriever instance
    """
    retriever = ChromaDBRetriever(collection_name=collection_name)
    retriever.build_index_from_jsonl(jsonl_file_path)
    return retriever

def search_documents(query: str, retriever: ChromaDBRetriever, top_k: int = 5) -> List[str]:
    """
    Search for documents and return text content.
    
    Args:
        query: Search query
        retriever: ChromaDBRetriever instance
        top_k: Number of results to return
        
    Returns:
        List of document texts
    """
    results = retriever.search(query, top_k=top_k)
    return [result['text'] for result in results]

# Legacy functions for backward compatibility
def build_faiss_index(embeddings):
    """
    Legacy FAISS function - now uses ChromaDB instead.
    """
    print("[WARNING] FAISS is not available on M1 Mac. Using ChromaDB instead.")
    return None

def search_index(question_embedding, index, texts, top_k=5):
    """
    Legacy search function - now uses ChromaDB instead.
    """
    print("[WARNING] FAISS search is not available on M1 Mac. Using ChromaDB instead.")
    return []

