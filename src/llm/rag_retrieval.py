import faiss
import numpy as np 

def build_faiss_index(embeddings):
    """
    Build faiss index 
    Args:
        embeddings: input embeddings
    Returns: 
        index
    """
    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

def search_index(question_embedding, index, texts, top_k=5):
    """
    Search index
    Args:
        questions_embedding: 
        index:
        texts:
        top_k: 5
    Return:
        result list: list of indices
    """
    question_embedding = question_embedding.reshape(1, -1)
    distances, indices = index.search(question_embedding, top_k)
    results = [texts[i] for i in indices[0]]
    return results

