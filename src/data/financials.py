import requests
import pandas as pd 
import os
import json
from typing import List, Dict
import yfinance as yf

TICKER = "NOG"
API_KEY = os.getenv("FMP_API_KEY")

def fetch_yahoo_finance_data():
    """
    Fetch free financial data from Yahoo Finance.
    This provides recent financial information without API costs.
    """
    print("[INFO] Fetching Yahoo Finance data for NOG...")
    
    try:
        # Get stock info
        stock = yf.Ticker("NOG")
        
        # Get financial statements
        income_stmt = stock.financials
        balance_sheet = stock.balance_sheet
        cash_flow = stock.cashflow
        
        # Get recent earnings
        earnings = stock.earnings
        
        # Get analyst info
        info = stock.info
        
        chunks = []
        
        # Create income statement chunks
        if not income_stmt.empty:
            for col in income_stmt.columns[:4]:  # Last 4 quarters
                quarter_data = income_stmt[col].dropna()
                if len(quarter_data) > 0 and isinstance(quarter_data, pd.Series):
                    chunk_text = f"""
Quarterly Income Statement - {col.strftime('%Y-%m-%d')}

Key Financial Metrics:
"""
                    for metric, value in quarter_data.head(10).items():
                        if pd.notna(value):
                            formatted_value = f"${value:,.0f}" if abs(value) >= 1000 else f"${value:.2f}"
                            chunk_text += f"- {metric}: {formatted_value}\n"
                    
                    chunks.append({
                        "text": chunk_text.strip(),
                        "metadata": {
                            "type": "financial",
                            "date": col.strftime('%Y-%m-%d'),
                            "statement": "income_statement",
                            "source": "yahoo_finance",
                            "ticker": "NOG"
                        }
                    })
        
        # Create balance sheet chunks
        if not balance_sheet.empty:
            for col in balance_sheet.columns[:4]:  # Last 4 quarters
                quarter_data = balance_sheet[col].dropna()
                if len(quarter_data) > 0 and isinstance(quarter_data, pd.Series):
                    chunk_text = f"""
Quarterly Balance Sheet - {col.strftime('%Y-%m-%d')}

Key Balance Sheet Items:
"""
                    for metric, value in quarter_data.head(10).items():
                        if pd.notna(value):
                            formatted_value = f"${value:,.0f}" if abs(value) >= 1000 else f"${value:.2f}"
                            chunk_text += f"- {metric}: {formatted_value}\n"
                    
                    chunks.append({
                        "text": chunk_text.strip(),
                        "metadata": {
                            "type": "financial",
                            "date": col.strftime('%Y-%m-%d'),
                            "statement": "balance_sheet",
                            "source": "yahoo_finance",
                            "ticker": "NOG"
                        }
                    })
        
        # Add company info
        if info:
            info_chunk = f"""
Company Information - NOG (Northern Oil and Gas)

Business Summary: {info.get('longBusinessSummary', 'N/A')}

Key Metrics:
- Market Cap: ${info.get('marketCap', 0):,.0f}
- Enterprise Value: ${info.get('enterpriseValue', 0):,.0f}
- P/E Ratio: {info.get('trailingPE', 'N/A')}
- Forward P/E: {info.get('forwardPE', 'N/A')}
- Price to Book: {info.get('priceToBook', 'N/A')}
- Debt to Equity: {info.get('debtToEquity', 'N/A')}
- Return on Equity: {info.get('returnOnEquity', 'N/A')}
- Profit Margins: {info.get('profitMargins', 'N/A')}
- Operating Margins: {info.get('operatingMargins', 'N/A')}

Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Employees: {info.get('fullTimeEmployees', 'N/A')}
"""
            
            chunks.append({
                "text": info_chunk.strip(),
                "metadata": {
                    "type": "company_info",
                    "date": "current",
                    "source": "yahoo_finance",
                    "ticker": "NOG"
                }
            })
        
        print(f"[INFO] Created {len(chunks)} Yahoo Finance chunks")
        return chunks
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch Yahoo Finance data: {e}")
        return []

def format_num(value):
    """Format numbers for better readability"""
    if pd.isna(value) or value is None:
        return "N/A"
    try:
        if abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    except:
        return str(value)
    
def fetch_quarterly_financials(statement_type: str) -> pd.DataFrame:
    """
    Fetch quarterly financial statements from Financial Modeling Prep API.
    
    Args:
        statement_type: 'income-statement', 'balance-sheet', or 'cash-flow-statement'
        
    Returns:
        DataFrame with quarterly financial data
    """
    if not API_KEY:
        print("[WARNING] No FMP API key found. Using Yahoo Finance data only.")
        return pd.DataFrame()
    
    url = f"https://financialmodelingprep.com/api/v3/{statement_type}/{TICKER}?period=quarter&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data:
            df = pd.DataFrame(data)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {statement_type}: {e}")
        return pd.DataFrame()

def create_financial_chunks():
    """
    Create comprehensive financial chunks for RAG.
    """
    print("[INFO] Creating financial chunks...")
    
    chunks = []
    
    # Add Yahoo Finance data (free)
    yahoo_chunks = fetch_yahoo_finance_data()
    chunks.extend(yahoo_chunks)
    
    # Add FMP data if API key is available
    if API_KEY:
        statements = ['income-statement', 'balance-sheet', 'cash-flow-statement']
        
        for statement in statements:
            df = fetch_quarterly_financials(statement)
            if not df.empty:
                # Process each quarter
                for _, row in df.head(8).iterrows():  # Last 8 quarters
                    chunk_text = f"""
Quarterly {statement.replace('-', ' ').title()} - {row.get('date', 'N/A')}

Key Financial Data:
"""
                    # Add key metrics based on statement type
                    if statement == 'income-statement':
                        metrics = ['revenue', 'grossProfit', 'operatingIncome', 'netIncome']
                    elif statement == 'balance-sheet':
                        metrics = ['totalAssets', 'totalLiabilities', 'totalEquity', 'cashAndCashEquivalents']
                    else:  # cash-flow-statement
                        metrics = ['operatingCashFlow', 'investingCashFlow', 'financingCashFlow', 'netIncome']
                    
                    for metric in metrics:
                        value = row.get(metric)
                        if value is not None:
                            formatted_value = format_num(value)
                            chunk_text += f"- {metric}: {formatted_value}\n"
                    
                    chunks.append({
                        "text": chunk_text.strip(),
                        "metadata": {
                            "type": "financial",
                            "date": row.get('date', 'N/A'),
                            "statement": statement,
                            "source": "financial_modeling_prep",
                            "ticker": "NOG"
                        }
                    })
    
    print(f"[INFO] Created {len(chunks)} total financial chunks")
    return chunks

def save_financial_chunks(chunks: List[Dict]):
    """Save financial chunks to file."""
    with open('data/chunks/enhanced_financial_chunks.json', 'w') as f:
        json.dump(chunks, f, indent=2)
    print(f"[INFO] Saved {len(chunks)} financial chunks to data/chunks/enhanced_financial_chunks.json")

if __name__ == '__main__':
    chunks = create_financial_chunks()
    save_financial_chunks(chunks)


