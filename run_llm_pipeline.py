from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from src.llm.rag_retrieval import build_faiss_index, search_index
from src.llm.llm_inference import generate_answers
import pandas as pd 
import json
import warnings
warnings.filterwarnings('ignore')

embeddingmodel = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

def run_rag_pipeline(question, documents, fundamentals_summary):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(documents, show_progress_bar=False)
    index = build_faiss_index(embeddings)
    question_embedding = model.encode([question])[0]
    context = search_index(question_embedding, index, documents, top_k=5)
    fullcontext = [fundamentals_summary] + context 
    return generate_answers(question, fullcontext)

def load_corpus(document):
    """
    Loads the JSONL corpus and converts to langChain document format.
    Args:
        document: jsonl file path.
    Returns:
        corpus: langchain format document. 
    """
    corpus = []
    with open(document, 'r') as f:
        for line in f:
            item = json.loads(line)
            corpus.append(Document(
                page_content=item['text'],
                metadata=item['metadata']
            ))
    return corpus

def create_faiss(documents):
    """
    Creates a faiss index from the documents. 
    Args:
        documents: documents to index on. 
    Returns:
        faiss index 
    """
    return FAISS.from_documents(documents, embeddingmodel)

def build_qa_chain(faissindex):
    """
    Build the QA chain 
    """
    retriever = faissindex.as_retriever(search_kwargs={"k":5})
    llm = ChatOpenAI(temperature=0.2, model_name='gpt-4')
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

def answer_questions(question, jsonlpath):
    documents = load_corpus(jsonlpath)
    faissindex = create_faiss(documents)
    qa_chain = build_qa_chain(faissindex)
    result = qa_chain(question)
    return result['result'], result['source_documents']

if __name__=='__main__':
    question = 'What is the latest P/E ratio of the company'
    jsonlpath = 'data/chunks/corpus.jsonl'
    answer, sources = answer_questions(question, jsonlpath)
    print("Answer:\n", answer)
    print("\nSources:\n", [doc.metadata for doc in sources])
