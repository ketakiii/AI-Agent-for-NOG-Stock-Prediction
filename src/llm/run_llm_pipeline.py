import os
import json
from tqdm import tqdm
from typing import List
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

class llm_pipeline:

    def __init__(self, modelname: str='all-MiniLM-L6-v2', index_save_path: str='data/chroma_db'):
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
        # Use ChromaDB instead of FAISS
        self.db = Chroma.from_documents(
            documents=documents, 
            embedding=self.embedding_model,
            persist_directory=self.index_save_path
        )
        print('ChromaDB index created with {} documents'.format(len(documents)))
    
    def save_index(self):
        if self.db:
            # ChromaDB automatically persists when created with persist_directory
            print(f'Index saved to {self.index_save_path}')
    
    def run(self, inputpath: str):
        documents = self.load_documents_from_jsonl(inputpath)
        self.build_index(documents)
        self.save_index()

if __name__=='__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Build and save vector db using ChromaDB')
    parser.add_argument('--input', type=str, required=True, help='Path to input JSONL file')
    parser.add_argument('--model', type=str, default='all-MiniLM-L6-v2', help='Hugging Face model for embeddings')
    parser.add_argument('--output', type=str, default='data/chroma_db', help='Directory to save the ChromaDB index')
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    builder = llm_pipeline(modelname=args.model, index_save_path=args.output)
    builder.run(args.input)