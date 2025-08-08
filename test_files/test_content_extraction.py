#!/usr/bin/env python3
"""
Test script to debug news content extraction
"""

import requests
from bs4 import BeautifulSoup
import time

def test_content_extraction(url, title, description):
    """Test content extraction for a single URL"""
    print(f"\n=== Testing: {title} ===")
    print(f"URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("Fetching URL...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content
            content_selectors = [
                'article', '.article-content', '.post-content', '.entry-content',
                '.content', '.main-content', '[role="main"]', '.story-body'
            ]
            
            content = None
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    print(f"Found content with selector: {selector}")
                    break
            
            if not content:
                content = soup.find('body')
                print("Using body as fallback")
            
            if content:
                text = content.get_text(separator=' ', strip=True)
                if text and isinstance(text, str):
                    text = ' '.join(text.split())
                    print(f"Extracted {len(text)} characters")
                    print(f"First 200 chars: {text[:200]}...")
                    return text[:1000] if len(text) > 200 else None
                else:
                    print("No text extracted")
            else:
                print("No content found")
        else:
            print(f"Failed to fetch: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_sample_urls():
    """Test a few sample URLs to see what's happening"""
    test_cases = [
        {
            "url": "https://www.businesswire.com/news/home/20241105005895/en/NOG-Announces-Third-Quarter-2024-Results-Achieves-Record-Oil-Production",
            "title": "NOG Announces Third Quarter 2024 Results",
            "description": "NOG Announces Third Quarter 2024 Results, Achieves Record Oil Production"
        },
        {
            "url": "https://seekingalpha.com/news/4101234-northern-oil-gas-q3-oil-volumes-estimated-increased-sequentially",
            "title": "Northern Oil and Gas Q3 oil volumes estimated to have increased sequentially",
            "description": "Northern Oil and Gas says Q3 oil volumes estimated to have increased sequentially"
        }
    ]
    
    for case in test_cases:
        result = test_content_extraction(case["url"], case["title"], case["description"])
        if result:
            print("✅ SUCCESS: Got real content")
        else:
            print("❌ FAILED: Using fallback content")
        time.sleep(2)  # Be respectful

if __name__ == "__main__":
    test_sample_urls() 