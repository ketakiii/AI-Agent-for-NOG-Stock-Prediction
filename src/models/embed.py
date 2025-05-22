import os 
import numpy as np
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key)

def get_news_feature_to_embed():
    new_df = pd.read_csv('data/NOG_news_2years.csv')
    content_list = (new_df['title'].fillna('') + '-' + new_df['description'].fillna('')).to_list()
    return content_list

def embed_news():
    model = SentenceTransformer()
    content_list = get_news_feature_to_embed()
    embeddings = model.encode(content_list, show_progress_bar=True)
    df_embeddings = pd.DataFrame(embeddings)
    return df_embeddings

def embed_text(texts):
    """
    Embed texts into np array
    Args:
        text: input text
    Return:
        embeddings 
    """
    embeddings = []
    for text in texts:
        response = client.embeddings.create(
            model = 'text-embedding-ada-002',
            input=text
        )
        embeddings.append(np.array(response.data[0].embedding, dtype=np.float32))
    return embeddings

def embed_image(image_path):
    """
    Embed images into np array
    Args:
        image_path: image path
    Return:
        embeddings 
    """
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
    response = client.embeddings.create(
        model='clip-vit-base-patch32',
        input=img_bytes
    ) 
    return np.array(response.data[0].embedding, dtype=np.float32)

if __name__=='__main__':
    sample_texts = ["Northern Oil & Gas stock rose today.", "Market forecast is positive."]
    embs = embed_text(sample_texts)
    print(f"Embedded {len(embs)} texts")