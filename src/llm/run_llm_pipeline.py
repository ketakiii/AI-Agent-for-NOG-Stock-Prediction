import os
import json
from tqdm import tqdm
from typing import List
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

class llm_pipeline:

    def __init__(self, modelname: str='all-MiniLM-L6-v2', index_save_path: str='saved_models/vector_store/faiss_index'):
        self.modelname = modelname
        self.index_save_path = index_save_path
        self.embedding_model = HuggingFaceEmbeddings(model_name=modelname)
        self.db = None

    def load_documents_from_jsonl(self, jsonlpath: str) -> List[Document]:
        documents = []
        with open(jsonlpath, 'r') as file:
            for line in tqdm(file, desc=f'Loading {jsonlpath}'):
                item = json.loads(line)
                metadata = item.get('metadata', {})
                doc = Document(page_content=item['text'], metadata=metadata)
                documents.append(doc)
        return documents
    
    def build_index(self, documents: List[Document]):
        self.db = FAISS.from_documents(documents, self.embedding_model)
        print('FAISS index created with {} documents'.format(len(documents)))
    
    def save_index(self):
        if self.db:
            self.db.save_local(self.index_save_path)
            print(f'Index saved to {self.index_save_path}')
    
    def run(self, inputpath: str):
        documents = self.load_documents_from_jsonl(inputpath)
        self.build_index(documents)
        self.save_index()

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Build and save vector db from FAISS index')
    parser.add_argument('--input', type=str, required=True, help='Path to input JSONL file')
    parser.add_argument('--model', type=str, default='all-MiniLM-L6-v2', help='Hugging Face model for embeddings')
    parser.add_argument('--output', type=str, default='saved_models/vector_store/faiss_index', help='Directory to save the FAISS index')
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    builder = llm_pipeline(modelname=args.model, index_save_path=args.output)
    builder.run(args.input)