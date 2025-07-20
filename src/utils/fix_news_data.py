import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urlparse
import re

def extract_article_content(url, title, description):
    """
    Extract article content from various news sources.
    """
    try:
        # Skip if it's a Google News redirect URL
        if 'news.google.com' in url:
            return description  # Use description as fallback
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try different content extraction strategies
        content_selectors = [
            'article',
            '.article-content',
            '.story-content',
            '.post-content',
            '.entry-content',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="story"]',
            'main',
            '.main-content'
        ]
        
        content = None
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Get text from the largest content element
                largest_element = max(elements, key=lambda x: len(x.get_text()))
                text = largest_element.get_text(strip=True)
                if len(text) > 200:  # Minimum content length
                    content = text
                    break
        
        # If no content found, try to get all paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
        
        # If still no content, use description
        if not content or len(content) < 100:
            content = description
            
        return content
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return description

def clean_text(text):
    """Clean and normalize text."""
    if not text or text == 'nan':
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def process_news_data():
    """Process the news CSV and extract proper content."""
    
    # Read the original CSV
    df = pd.read_csv('data/NOG_news_2years.csv')
    
    print(f"Processing {len(df)} news articles...")
    
    # Clean existing data
    df['title'] = df['title'].apply(clean_text)
    df['description'] = df['description'].apply(clean_text)
    df['publisher'] = df['publisher'].apply(clean_text)
    
    # Extract content for articles that don't have it
    new_content = []
    for idx, row in df.iterrows():
        if pd.isna(row['content']) or row['content'] == '' or row['content'] == 'nan':
            print(f"Extracting content for: {row['title'][:50]}...")
            content = extract_article_content(row['url'], row['title'], row['description'])
            new_content.append(content)
            time.sleep(1)  # Be respectful to servers
        else:
            new_content.append(row['content'])
    
    df['content'] = new_content
    
    # Save the enhanced data
    df.to_csv('data/NOG_news_enhanced.csv', index=False)
    
    # Create chunks for RAG
    news_chunks = []
    for idx, row in df.iterrows():
        if row['content'] and row['content'] != 'nan' and len(row['content']) > 50:
            # Split content into chunks if too long
            content = row['content']
            if len(content) > 2000:
                # Simple chunking by sentences
                sentences = content.split('. ')
                chunks = []
                current_chunk = ""
                for sentence in sentences:
                    if len(current_chunk + sentence) < 2000:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks = [content]
            
            for chunk_idx, chunk in enumerate(chunks):
                news_chunks.append({
                    "text": chunk,
                    "metadata": {
                        "type": "news",
                        "date": row['date'],
                        "title": row['title'],
                        "publisher": row['publisher'],
                        "url": row['url'],
                        "chunk_id": f"{idx}_{chunk_idx}"
                    }
                })
    
    # Save chunks
    with open('data/chunks/news_chunks_enhanced.json', 'w', encoding='utf-8') as f:
        json.dump(news_chunks, f, indent=2)
    
    print(f"Created {len(news_chunks)} news chunks")
    print(f"Enhanced data saved to data/NOG_news_enhanced.csv")
    print(f"Chunks saved to data/chunks/news_chunks_enhanced.json")

if __name__ == "__main__":
    process_news_data() 