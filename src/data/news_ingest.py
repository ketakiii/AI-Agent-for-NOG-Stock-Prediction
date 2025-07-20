from gnews import GNews
import pandas as pd
import time
from typing import List
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

queries = [
    "Northern Oil and Gas",
    "NOG stock",
    "Northern Oil and Gas earnings",
    "Northern Oil & Gas Inc",
    "NOG Q1 results",
    "NOG Q2 results",
    "NOG Q3 results",
    "NOG Q4 results",
    "NOG quarterly report",
    "Northern Oil and Gas acquisition",
    "NOG financial results",
    "Northern Oil and Gas dividend"
]

articles = []
seen_urls = set()

def create_enhanced_content(title: str, description: str, source: str, date: str, url: str) -> str:
    """
    Create enhanced content from available metadata without URL extraction.
    This approach is more reliable and doesn't violate website terms.
    
    Args:
        title: Article title
        description: Article description/summary
        source: News source
        date: Publication date
        url: URL (for reference only)
        
    Returns:
        Enhanced content string
    """
    # Clean and format the inputs
    title = str(title).strip() if title and str(title) != 'nan' else ""
    description = str(description).strip() if description and str(description) != 'nan' else ""
    source = str(source).strip() if source and str(source) != 'nan' else "Unknown Source"
    date = str(date).strip() if date and str(date) != 'nan' else ""
    
    # Create rich content from available information
    content_parts = []
    
    # Add title
    if title:
        content_parts.append(f"Title: {title}")
    
    # Add description/summary
    if description:
        content_parts.append(f"Summary: {description}")
    
    # Add source and date for context
    if source and date:
        content_parts.append(f"Source: {source} | Date: {date}")
    elif source:
        content_parts.append(f"Source: {source}")
    elif date:
        content_parts.append(f"Date: {date}")
    
    # Add URL for reference (but don't extract content from it)
    if url and str(url) != 'nan':
        content_parts.append(f"Reference: {url}")
    
    # Combine all parts
    enhanced_content = "\n".join(content_parts)
    
    # If we have meaningful content, return it
    if len(enhanced_content.strip()) > 50:
        return enhanced_content
    else:
        return f"NOG News: {title}" if title else "NOG News Article"

def fetch_nog_news(period: str = '2y', delay: float = 1.0) -> pd.DataFrame:
    """
    Fetches news articles related to Northern Oil and Gas stock using GNews.

    Args:
        period (str): GNews period (e.g., '2y', '12m', '7d').
        delay (float): Delay between queries to avoid throttling.

    Returns:
        pd.DataFrame: DataFrame containing deduplicated news articles with enhanced content.
    """
    gnews = GNews(language='en', country='US', period=period, max_results=100)
    
    for query in queries:
        print(f"[INFO] Fetching news for query: '{query}'")
        try:
            results = gnews.get_news(query)
            if results:
                for article in results:
                    if article['url'] not in seen_urls:
                        seen_urls.add(article['url'])
                        
                        # Extract enhanced content
                        enhanced_content = create_enhanced_content(
                            article.get('title', ''), 
                            article.get('description', ''), 
                            article.get('publisher', {}).get('title', 'Unknown'), 
                            article.get('published date', ''), 
                            article.get('url', '')
                        )
                        
                        articles.append({
                            'date': article['published date'],
                            'title': article['title'],
                            'description': article['description'],
                            'content': enhanced_content,
                            'url': article['url'],
                            'publisher': article['publisher']['title']
                        })
                        
                        # Add delay to be respectful to servers
                        time.sleep(0.5)
                    
        except Exception as e:
            print(f"[WARNING] Failed to fetch for '{query}': {e}")
        time.sleep(delay)
    
    df = pd.DataFrame(articles)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], format='mixed').dt.date
        df = df.sort_values(by='date')
    return df

def create_enhanced_news_chunks(df: pd.DataFrame) -> List[dict]:
    """
    Create enhanced news chunks with better content for RAG.
    
    Args:
        df: DataFrame with news articles
        
    Returns:
        List of enhanced news chunks
    """
    chunks = []
    
    for _, row in df.iterrows():
        # Create a more detailed chunk
        chunk_text = f"""
Date: {row['date']}
Source: {row['publisher']}
Title: {row['title']}

{row['content']}

URL: {row['url']}
        """.strip()
        
        chunk = {
            "text": chunk_text,
            "metadata": {
                "type": "news",
                "date": str(row['date']),
                "title": row['title'],
                "source": row['publisher'],
                "url": row['url'],
                "ticker": "NOG"
            }
        }
        chunks.append(chunk)
    
    return chunks

def run_news_data_pipeline():
    """Enhanced news data pipeline that creates better chunks for RAG."""
    try:
        # Load existing news data
        old_news_df = pd.read_csv('/opt/airflow/project/data/NOG_news_2years.csv')
        print(f"[INFO] Loaded {len(old_news_df)} existing news articles")
    except FileNotFoundError:
        old_news_df = pd.DataFrame()
        print("[INFO] No existing news file found, starting fresh")
    
    # Fetch new news
    updated_news_df = fetch_nog_news(period='7d')
    print(f"[INFO] Fetched {len(updated_news_df)} new news articles")
    
    # Combine old and new data
    if not old_news_df.empty:
        data = pd.concat([old_news_df, updated_news_df])
        data = data.drop_duplicates(subset=['url'])  # Remove duplicates
    else:
        data = updated_news_df
    
    # Save the raw data
    data.to_csv('/opt/airflow/project/data/NOG_news_2years.csv', index=False)
    print(f"[INFO] Saved {len(data)} total news articles to data/NOG_news_2years.csv")

    # Create enhanced chunks
    enhanced_chunks = create_enhanced_news_chunks(data)
    
    # Save enhanced chunks
    import json
    with open('/opt/airflow/project/data/chunks/enhanced_news_chunks.json', 'w') as f:
        json.dump(enhanced_chunks, f, indent=2)
    
    print(f"[INFO] Created {len(enhanced_chunks)} enhanced news chunks")
    
    return data, enhanced_chunks

if __name__ == '__main__':
    run_news_data_pipeline()

