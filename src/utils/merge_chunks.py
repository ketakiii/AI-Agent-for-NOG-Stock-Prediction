import json 
import os
from typing import List, Dict
import pandas as pd

def load_json_chunks(file_path: str) -> List[Dict]:
    """Load chunks from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {file_path}: {e}")
        return []

def load_jsonl_chunks(file_path: str) -> List[Dict]:
    """Load chunks from a JSONL file."""
    chunks = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))
        return chunks
    except FileNotFoundError:
        print(f"[WARNING] File not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSONL in {file_path}: {e}")
        return []

def merge_all_chunks() -> List[Dict]:
    """
    Merge all available chunks into a single corpus for RAG.
    
    Returns:
        List of all chunks with consistent format
    """
    all_chunks = []
    
    # Load enhanced news chunks
    news_chunks = load_json_chunks('data/chunks/enhanced_news_chunks.json')
    print(f"[INFO] Loaded {len(news_chunks)} enhanced news chunks")
    all_chunks.extend(news_chunks)
    
    # Load enhanced financial chunks
    financial_chunks = load_json_chunks('data/chunks/enhanced_financial_chunks.json')
    print(f"[INFO] Loaded {len(financial_chunks)} enhanced financial chunks")
    all_chunks.extend(financial_chunks)
    
    # Load existing corpus chunks (fallback)
    existing_corpus = load_jsonl_chunks('data/chunks/corpus.jsonl')
    print(f"[INFO] Loaded {len(existing_corpus)} existing corpus chunks")
    
    # Only add existing chunks if we don't have enhanced versions
    if len(all_chunks) == 0:
        print("[WARNING] No enhanced chunks found, using existing corpus")
        all_chunks.extend(existing_corpus)
    
    # Remove duplicates based on text content
    seen_texts = set()
    unique_chunks = []
    
    for chunk in all_chunks:
        text = chunk.get('text', '').strip()
        if text and text not in seen_texts:
            seen_texts.add(text)
            unique_chunks.append(chunk)
    
    print(f"[INFO] Total unique chunks after deduplication: {len(unique_chunks)}")
    
    return unique_chunks

def create_enhanced_corpus():
    """
    Create an enhanced corpus with all available data sources.
    """
    # Merge all chunks
    all_chunks = merge_all_chunks()
    
    if not all_chunks:
        print("[ERROR] No chunks available to create corpus")
        return
    
    # Save as JSONL for the RAG pipeline
    with open('data/chunks/enhanced_corpus.jsonl', 'w') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + '\n')
    
    print(f"[INFO] Created enhanced corpus with {len(all_chunks)} chunks")
    print("[INFO] Saved to: data/chunks/enhanced_corpus.jsonl")
    
    # Create a summary
    chunk_types = {}
    for chunk in all_chunks:
        chunk_type = chunk.get('metadata', {}).get('type', 'unknown')
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
    
    print("\n[INFO] Corpus Summary:")
    for chunk_type, count in chunk_types.items():
        print(f"  - {chunk_type}: {count} chunks")
    
    return all_chunks

def validate_corpus_quality(chunks: List[Dict]) -> Dict:
    """
    Validate the quality of the corpus chunks.
    
    Args:
        chunks: List of chunks to validate
        
    Returns:
        Dictionary with validation metrics
    """
    metrics = {
        'total_chunks': len(chunks),
        'avg_text_length': 0,
        'chunks_with_metadata': 0,
        'chunk_types': {},
        'recent_chunks': 0
    }
    
    if not chunks:
        return metrics
    
    total_length = 0
    for chunk in chunks:
        text = chunk.get('text', '')
        total_length += len(text)
        
        if 'metadata' in chunk:
            metrics['chunks_with_metadata'] += 1
            
            chunk_type = chunk['metadata'].get('type', 'unknown')
            metrics['chunk_types'][chunk_type] = metrics['chunk_types'].get(chunk_type, 0) + 1
            
            # Check for recent chunks (last 2 years)
            date_str = chunk['metadata'].get('date', '')
            if date_str:
                try:
                    date = pd.to_datetime(date_str)
                    if date.year >= 2023:
                        metrics['recent_chunks'] += 1
                except:
                    pass
    
    metrics['avg_text_length'] = total_length / len(chunks)
    
    return metrics

if __name__ == "__main__":
    # Create enhanced corpus
    chunks = create_enhanced_corpus()
    
    if chunks:
        # Validate quality
        metrics = validate_corpus_quality(chunks)
        print(f"\n[INFO] Corpus Quality Metrics:")
        print(f"  - Total chunks: {metrics['total_chunks']}")
        print(f"  - Average text length: {metrics['avg_text_length']:.0f} characters")
        print(f"  - Chunks with metadata: {metrics['chunks_with_metadata']}")
        print(f"  - Recent chunks (2023+): {metrics['recent_chunks']}")
        
        if metrics['avg_text_length'] < 100:
            print("[WARNING] Average chunk length is very short. Consider improving chunking strategy.")
        
        if metrics['recent_chunks'] < metrics['total_chunks'] * 0.5:
            print("[WARNING] Less than 50% of chunks are from recent years. Consider updating data sources.")