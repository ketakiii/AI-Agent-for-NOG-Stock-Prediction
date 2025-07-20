#!/usr/bin/env python3
"""
Build comprehensive RAG corpus for NOG analysis.
Combines news, financial data, and other sources into a single JSONL file.
"""

import json
import pandas as pd
import os
from typing import List, Dict, Any
import re

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text or text == 'nan' or pd.isna(text):
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', str(text).strip())
    return text

def load_news_data() -> List[Dict[str, Any]]:
    """Load and process news data."""
    print("Loading news data...")
    
    news_chunks = []
    
    # Load news chunks
    if os.path.exists('data/chunks/news_chunks.json'):
        with open('data/chunks/news_chunks.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        for item in news_data:
            if item['text'] and len(item['text'].strip()) > 20:
                news_chunks.append({
                    'text': clean_text(item['text']),
                    'metadata': {
                        'type': 'news',
                        'date': item['metadata']['date'],
                        'title': clean_text(item['metadata']['title']),
                        'publisher': clean_text(item['metadata']['publisher']),
                        'url': item['metadata']['url'],
                        'source': 'news'
                    }
                })
    
    print(f"Loaded {len(news_chunks)} news chunks")
    return news_chunks

def load_financial_data() -> List[Dict[str, Any]]:
    """Load and process financial data."""
    print("Loading financial data...")
    
    financial_chunks = []
    
    # Load financial fundamentals if available
    if os.path.exists('data/NOG_financials.csv'):
        try:
            df = pd.read_csv('data/NOG_financials.csv')
            
            # Create chunks from financial data
            for idx, row in df.iterrows():
                # Create a comprehensive financial summary
                financial_text = f"Financial Data for {row.get('date', 'Unknown Date')}: "
                
                # Add key financial metrics
                metrics = []
                for col in df.columns:
                    if col != 'date' and pd.notna(row[col]):
                        value = row[col]
                        if isinstance(value, (int, float)):
                            if value > 1e6:
                                value = f"${value/1e6:.1f}M"
                            elif value > 1e3:
                                value = f"${value/1e3:.1f}K"
                            else:
                                value = f"${value:.2f}"
                        metrics.append(f"{col}: {value}")
                
                if metrics:
                    financial_text += "; ".join(metrics)
                    financial_chunks.append({
                        'text': financial_text,
                        'metadata': {
                            'type': 'financial',
                            'date': str(row.get('date', '')),
                            'source': 'financials'
                        }
                    })
        except Exception as e:
            print(f"Error loading financial data: {e}")
    
    print(f"Loaded {len(financial_chunks)} financial chunks")
    return financial_chunks

def load_earnings_data() -> List[Dict[str, Any]]:
    """Load and process earnings data."""
    print("Loading earnings data...")
    
    earnings_chunks = []
    
    # Load earnings data if available
    if os.path.exists('data/NOG_earnings.csv'):
        try:
            df = pd.read_csv('data/NOG_earnings.csv')
            
            for idx, row in df.iterrows():
                earnings_text = f"Earnings Report for {row.get('date', 'Unknown Date')}: "
                
                metrics = []
                for col in df.columns:
                    if col != 'date' and pd.notna(row[col]):
                        value = row[col]
                        if isinstance(value, (int, float)):
                            if value > 1e6:
                                value = f"${value/1e6:.1f}M"
                            elif value > 1e3:
                                value = f"${value/1e3:.1f}K"
                            else:
                                value = f"${value:.2f}"
                        metrics.append(f"{col}: {value}")
                
                if metrics:
                    earnings_text += "; ".join(metrics)
                    earnings_chunks.append({
                        'text': earnings_text,
                        'metadata': {
                            'type': 'earnings',
                            'date': str(row.get('date', '')),
                            'source': 'earnings'
                        }
                    })
        except Exception as e:
            print(f"Error loading earnings data: {e}")
    
    print(f"Loaded {len(earnings_chunks)} earnings chunks")
    return earnings_chunks

def create_company_overview() -> List[Dict[str, Any]]:
    """Create company overview and background information."""
    print("Creating company overview...")
    
    overview_chunks = [
        {
            'text': """Northern Oil and Gas (NOG) is a publicly traded independent energy company focused on the acquisition, exploration, and development of oil and gas properties in the United States. The company primarily operates in the Williston Basin in North Dakota and Montana, as well as the Permian Basin in Texas and New Mexico. NOG follows a non-operated business model, partnering with established operators to develop oil and gas assets while minimizing operational risks and capital requirements.""",
            'metadata': {
                'type': 'overview',
                'source': 'company_background'
            }
        },
        {
            'text': """NOG's business strategy focuses on acquiring high-quality, long-lived oil and gas properties with predictable production profiles. The company targets assets with low decline rates, strong cash flow generation, and significant development upside. NOG typically acquires working interests in producing wells and undeveloped acreage, allowing it to participate in future drilling programs without bearing the full cost and operational risk of being the operator.""",
            'metadata': {
                'type': 'strategy',
                'source': 'company_background'
            }
        },
        {
            'text': """The company's primary operating areas include the Williston Basin (Bakken/Three Forks formations) and the Permian Basin (Wolfcamp, Bone Spring, and Delaware formations). These are among the most prolific oil-producing regions in the United States, with significant remaining reserves and development potential. NOG's diversified portfolio across multiple basins helps reduce geographic concentration risk.""",
            'metadata': {
                'type': 'operations',
                'source': 'company_background'
            }
        }
    ]
    
    print(f"Created {len(overview_chunks)} overview chunks")
    return overview_chunks

def build_comprehensive_corpus() -> None:
    """Build comprehensive RAG corpus from all available sources."""
    print("Building comprehensive RAG corpus...")
    
    # Load all data sources
    all_chunks = []
    
    # Add company overview
    all_chunks.extend(create_company_overview())
    
    # Add news data
    all_chunks.extend(load_news_data())
    
    # Add financial data
    all_chunks.extend(load_financial_data())
    
    # Add earnings data
    all_chunks.extend(load_earnings_data())
    
    # Filter out empty or very short chunks
    filtered_chunks = []
    for chunk in all_chunks:
        if chunk['text'] and len(chunk['text'].strip()) > 20:
            filtered_chunks.append(chunk)
    
    print(f"Total chunks after filtering: {len(filtered_chunks)}")
    
    # Save as JSONL
    output_file = 'data/chunks/comprehensive_corpus.jsonl'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in filtered_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
    
    print(f"Comprehensive corpus saved to: {output_file}")
    
    # Print statistics
    source_counts = {}
    type_counts = {}
    
    for chunk in filtered_chunks:
        source = chunk['metadata'].get('source', 'unknown')
        doc_type = chunk['metadata'].get('type', 'unknown')
        
        source_counts[source] = source_counts.get(source, 0) + 1
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    
    print("\nCorpus Statistics:")
    print("Source breakdown:")
    for source, count in source_counts.items():
        print(f"  {source}: {count}")
    
    print("\nDocument type breakdown:")
    for doc_type, count in type_counts.items():
        print(f"  {doc_type}: {count}")

if __name__ == "__main__":
    build_comprehensive_corpus() 