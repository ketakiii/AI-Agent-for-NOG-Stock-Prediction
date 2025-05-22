from gnews import GNews
import pandas as pd
import time
from typing import List

queries = [
    "Northern Oil and Gas",
    "NOG stock",
    "Northern Oil and Gas earnings",
    "Northern Oil & Gas Inc",
    "NOG Q1 results",
    "NOG Q2 results",
    "NOG Q3 results",
    "NOG Q4 results",
    "NOG quarterly report"
]

articles = []
seen_urls = set()

def fetch_nog_news(period: str = '2y', delay: float = 1.0) -> pd.DataFrame:
    """
    Fetches news articles related to Northern Oil and Gas stock using GNews.

    Args:
        save_path (str, optional): Path to save CSV file. If None, file is not saved.
        period (str): GNews period (e.g., '2y', '12m', '7d').
        delay (float): Delay between queries to avoid throttling.

    Returns:
        pd.DataFrame: DataFrame containing deduplicated news articles.
    """
    gnews = GNews(language='en', country='US', period=period, max_results=100)
    for query in queries:
        print(f"[INFO] Fetching news for query: '{query}'")
        try:
            results = gnews.get_news(query)
            for article in results:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    articles.append({
                        'date': article['published date'],
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['url'],
                        'publisher': article['publisher']['title']
                    })
        except Exception as e:
            print(f"[WARNING] Failed to fetch for '{query}': {e}")
        time.sleep(delay)
    df = pd.DataFrame(articles)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.date
        df = df.sort_values(by='date')
    return df


def run_news_data_pipeline():
    old_news_df = pd.read_csv('data/NOG_news_2years.csv')
    updated_news_df = fetch_nog_news(period='7d')
    data = pd.concat([old_news_df, updated_news_df])
    data.to_csv('data/NOG_news_2years.csv')

# if __name__=='__main__':

