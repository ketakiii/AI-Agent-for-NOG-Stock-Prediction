import os
import logging
from rag_retrieval import ChromaDBRetriever
from llm_inference import generate_answers

# Ensure the API key is available
# Make sure you have your OPENAI_API_KEY set in your environment

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("rag_evaluation.log"),
            logging.StreamHandler()
        ]
    )

def run_evaluation():
    """
    Runs a simple evaluation of the RAG pipeline.
    """
    setup_logging()
    logging.info("--- Starting RAG Pipeline Evaluation ---")

    # 1. Initialize the retriever
    try:
        retriever = ChromaDBRetriever(collection_name="nog_corpus", persist_directory="data/chroma_db")
        logging.info("Successfully loaded ChromaDB retriever.")
        logging.info(f"Collection stats: {retriever.get_collection_stats()}")
    except Exception as e:
        logging.error(f"Error initializing retriever: {e}")
        logging.error("Please ensure you have built the index first using 'run_llm_pipeline.py' or 'rag_retrieval.py'.")
        return

    # 2. Define a test set of questions
    test_questions = [
        "What were the key financial results for NOG in the last quarter?",
        "What are the latest developments regarding Northern Oil and Gas acquisitions?",
        "What is the company's outlook on future production?",
        "Are there any recent news about NOG's dividend policy?"
    ]

    # 3. Run the pipeline for each question
    for i, question in enumerate(test_questions):
        logging.info(f"--- Question {i+1}: {question} ---")

        # a. Retrieve context
        try:
            retrieved_docs = retriever.search(question, top_k=5)
            if not retrieved_docs:
                logging.warning("No relevant context found.")
                continue
            
            context_texts = [doc['text'] for doc in retrieved_docs]
            logging.info(f"[Retrieved Context - Top {len(context_texts)} docs]:")
            for j, doc in enumerate(retrieved_docs):
                logging.info(f"  {j+1}. (Distance: {doc['distance']:.4f}) {doc['text'][:150].strip()}...")

        except Exception as e:
            logging.error(f"Error during context retrieval: {e}")
            continue

        # b. Generate answer
        try:
            answer = generate_answers(question, context_texts)
            logging.info(f"[Generated Answer]:\n{answer}")
        except Exception as e:
            logging.error(f"Error during answer generation: {e}")

    logging.info("--- Evaluation Complete ---")

if __name__ == '__main__':
    run_evaluation()
