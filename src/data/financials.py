import requests
import pandas as pd 
from yfinance import Ticker
import os

TICKER = 'NOG'
BASE_FMP_URL = 'https://financialmodelingprep.com/api/v3'
FMP_API_KEY = os.getenv("FMP_API_KEY")

api_key = os.getenv("AV_API_KEY")

def get_fmp_ratios_over_time(ticker):
    url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?period=quarter&apikey={FMP_API_KEY}"
    res = requests.get(url)
    data = res.json()
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    return df[['date', 'priceEarningsRatio', 'priceToBookRatio', 'returnOnEquity', 'debtEquityRatio']]

def get_yahoo_fundamentals(ticker_symbol):
    ticker = Ticker(ticker_symbol)
    info = ticker.info
    fundamentals = {
        'symbol': ticker_symbol,
        'pe_ratio': info.get('trailingPE'),
        'market_cap': info.get('marketCap'),
        'price_to_book': info.get('priceToBook'),
        'return_on_equity': info.get('returnOnEquity'),
        'debt_to_equity': info.get('debtToEquity'),
        'sector': info.get('sector'),
        'industry': info.get('industry')
    }
    return pd.DataFrame([fundamentals])

def fetch_quarterly_financials(statement_type):
    function_map = {
        "income-statement": "INCOME_STATEMENT",
        "balance-sheet-statement": "BALANCE_SHEET"
    }
    function = function_map[statement_type]
    url = f"https://www.alphavantage.co/query?function={function}&symbol={TICKER}&apikey={api_key}"
    res = requests.get(url)
    data = res.json()
    if 'quarterlyReports' not in data:
        raise ValueError(f"Error in API response: {data}")
    df = pd.DataFrame(data['quarterlyReports'])
    df['date'] = pd.to_datetime(df['fiscalDateEnding'])
    return df

def combine():
    # fundamentals from Yahoo 

    # Fetch FMP quarterly income statement and balance sheet
    income_df = fetch_quarterly_financials('income-statement')
    balance_df = fetch_quarterly_financials('balance-sheet-statement')

    # Merge financial statements 
    merged_df = pd.merge(income_df, balance_df, on='date', suffixes=('_income', '_balance'))
    
    # sort and save 
    merged_df.sort_values('date', ascending=False, inplace=True)
    merged_df.to_csv('data/financials.csv', index=False)


if __name__=='__main__':
    # combine()
    combine()


