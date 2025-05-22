from sentence_transformers import SentenceTransformer
from src.llm.rag_retrieval import build_faiss_index, search_index
from src.llm.llm_inference import generate_answers
import pandas as pd 

def run_rag_pipeline(question, documents):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(documents, show_progress_bar=False)
    index = build_faiss_index(embeddings)
    question_embedding = model.encode([question])[0]
    context = search_index(question_embedding, index, documents, top_k=5)
    return generate_answers(question, context)

def load_news_document(csvpath):
    """
    Load and format csv news data into chunks for RAG.
    Args:
        csvpath : path to the csv 
    Return:
        list of document strings 
    """
    df = pd.read_csv(csvpath)
    df['description'] = df['description'].fillna('')
    documents = [
        f'Date: {row["date"]}. Title: {row["title"]}. Description {row["description"]}'
        for _, row in df.iterrows()
    ]
    return documents

if __name__=='__main__':
    documents = load_news_document('data/NOG_news_2years.csv')
    question = 'Should i not invest in NOG stock and why?'
    answer = run_rag_pipeline(question, documents)
    print(answer)