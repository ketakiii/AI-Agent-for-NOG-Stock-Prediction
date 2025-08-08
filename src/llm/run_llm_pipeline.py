import os
import argparse
from rag_retrieval import ChromaDBRetriever

def run_indexing(input_file: str, collection_name: str, persist_directory: str):
    """
    Builds or updates a ChromaDB index from a JSONL file.
    """
    print(f"--- Starting Index Build for collection '{collection_name}' ---")
    
    # Initialize the retriever, which connects to or creates the collection
    retriever = ChromaDBRetriever(
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    
    # Build the index from the specified file
    retriever.build_index_from_json(input_file)
    
    print("--- Indexing Complete ---")
    stats = retriever.get_collection_stats()
    print(f"Collection stats: {stats}")

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Build a ChromaDB vector index from a JSONL file.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input JSONL file.')
    parser.add_argument('--collection', type=str, default='nog_corpus', help='Name of the ChromaDB collection.')
    parser.add_argument('--db_path', type=str, default='data/chroma_db', help='Directory to persist the ChromaDB index.')
    
    args = parser.parse_args()
    
    # Ensure the database directory exists
    os.makedirs(args.db_path, exist_ok=True)
    
    run_indexing(
        input_file=args.input,
        collection_name=args.collection,
        persist_directory=args.db_path
    )