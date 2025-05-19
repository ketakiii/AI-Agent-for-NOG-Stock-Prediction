import os 
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key)

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