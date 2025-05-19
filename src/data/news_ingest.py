from dotenv import load_dotenv
import requests
import os

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news_query(query, page_size=50):
    """
    Fetch news using the api and the input query for 50 page sizes
    Args:
        query: query to filter on
        page_size: result page numbers
    Return:
        contents list of the fetched news
    """
    params = {
    "q": query,
    "apiKey": NEWS_API_KEY,
    "pageSize": page_size,
    "sortBy": "publishedAt"
    }   
    res = requests.get("https://newsapi.org/v2/everything", params=params)
    res.raise_for_status()
    articles = res.json().get('articles', [])
    contents = []
    for art in articles:
        content = art.get('content') or art.get('description') or ''
        if content:
            contents.append(content)
    return contents

def fetch_all_news():
    nog_articles = fetch_news_query(query='"Northern Oil and Gas" OR "NOG Inc" OR "NOG stock"')
    sector_articles = fetch_news_query(query='"oil stock" OR "energy sector" OR "crude oil"')
    all_articles = nog_articles + sector_articles
    return all_articles

if __name__=='__main__':
    news = fetch_all_news()