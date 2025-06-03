# src/llm/query_classifier.py

from typing import Dict
from sentence_transformers import SentenceTransformer, util

class QueryClassifier:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.intent_templates = {
            "pe_ratio": [
                "What is the latest P/E ratio?",
                "Tell me the price to earnings ratio of NOG.",
                "How is the company valued?",
                "What's the valuation multiple?"
            ],
            "roe": [
                "What is the return on equity?",
                "How efficient is the company at generating profit from equity?",
                "Show me ROE for NOG"
            ],
            "debt_to_equity": [
                "How leveraged is NOG?",
                "Show debt to equity ratio",
                "What is the company's financial leverage?"
            ],
            "news": [
                "What happened recently?",
                "Any recent news about NOG?",
                "Latest updates or events?"
            ],
            "financials": [
                "How was the quarterly performance?",
                "What are the key financials this year?",
                "Give me a financial summary"
            ]
        }

        self.intent_embeddings = {
            intent: self.model.encode(templates, convert_to_tensor=True)
            for intent, templates in self.intent_templates.items()
        }

    def classify_query(self, user_query: str) -> str:
        query_embedding = self.model.encode(user_query, convert_to_tensor=True)
        best_intent = None
        best_score = -1

        for intent, embeddings in self.intent_embeddings.items():
            similarity = util.max_cos_sim(query_embedding, embeddings).item()
            if similarity > best_score:
                best_score = similarity
                best_intent = intent

        return best_intent if best_score > 0.5 else "general"
