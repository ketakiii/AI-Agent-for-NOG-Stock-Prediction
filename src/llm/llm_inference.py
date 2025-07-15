from openai import OpenAI
import os 
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

api_key = os.getenv("OPENAI_API_KEY")

# if not api_key:
#     raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key)

def generate_answers(question, context_texts):
    """
    Generate answers based on the question and the context texts
    Args:
        question
        context_text
    Return:
        response
    """
    context = '\n\n'.join(context_texts)
    prompt = f'Answer the question based on the context below: \n{context}\n\nQuestion: {question}\nAnswer:'
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{'role':'user', 'content':prompt}], 
        max_tokens=256,
        temperature=0.2
    )
    print(response.choices[0].message.content)
    # return response.choices[0].message['content']

if __name__=='__main__':
    question = "What is the current forecast for Northern Oil & Gas?"
    sample_context = [
        "Date: 2025-05-18, Close: 25.3, XGBoost Prediction: 26.1",
        "Oil prices have been rising steadily this month."
    ]
    answer = generate_answers(question, sample_context)
    print("Answer:", answer)