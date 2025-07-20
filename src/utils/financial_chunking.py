import pandas as pd
import re
from datetime import datetime
import json

path = 'data/financial_chunks.txt'

alldata = []
# Step 2: Extract metrics with regex
def extract_value(pattern, text, cast_func=str, default=None):
    match = re.search(pattern, text)
    return cast_func(match.group(1).replace(',', '')) if match else default

with open(path, 'r') as file:
    content = file.read().replace('\n', '')  # Remove all newlines
    lines = content.split('|')               # Split using '|' as line break
    for line in lines:
        clean_text = line.strip('"').replace('        ', ' ').replace('**', '').replace(' -', '\n-').replace(' - ', '')
        date_match = re.search(r'As of (\d{4}-\d{2}-\d{2})', clean_text)
        try:
            date_str = date_match.group(1)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            date_obj = None
            print(clean_text)
        revenue = extract_value(r'Total revenue.*?\$([\d\.]+[MB])', clean_text)
        gross_profit = extract_value(r'gross profit.*?\$([\d\.]+[MB])', clean_text)
        op_income = extract_value(r'operating income.*?\$([\d\.]+[MB])', clean_text)
        net_income = extract_value(r'Net income.*?\$([\d\.]+[MB])', clean_text)
        ebitda = extract_value(r'EBITA.*?\$([\d\.]+[MB])', clean_text)
        ebit = extract_value(r'EBIT of.*?\$([\d\.]+[MB])', clean_text)
        sga = extract_value(r'spent.*?\$([\d\.]+[MB]) on SG&A', clean_text)
        interest = extract_value(r'interest expenses.*?\$([\d\.]+[MB])', clean_text)
        assets = extract_value(r'Total assets.*?\$([\d\.]+[MB])', clean_text)
        curr_assets = extract_value(r'current assets.*?\$([\d\.]+[MB])', clean_text)
        cash = extract_value(r'cash.*?\$([\d\.]+[MB])', clean_text)
        lt_debt = extract_value(r'Long-term debt.*?\$([\d\.]+[MB])', clean_text)
        liabilities = extract_value(r'total liabilities.*?\$([\d\.]+[MB])', clean_text)
        equity = extract_value(r'Shareholder equity.*?\$([\d\.]+[MB])', clean_text)
        shares = extract_value(r'(\d+\.?\d*)M shares', clean_text, float)
        try:
            pe_ratio = extract_value(r'P/E: ([\d\.]+)', clean_text, float)
        except:
            pe_ratio = None
        try:
            roe = extract_value(r'ROE: ([\d\.]+)', clean_text, float)
        except:
            roe = None
        try:
            de_ratio = extract_value(r'Debt to equity: ([\d\.]+)', clean_text, float)
        except:
            de_ratio = None
        
        json_output = {
        "text": clean_text.strip(),
        "metadata": {
            "type": "financials",
            "quarter": "Q1",
            "year": date_obj.year if date_obj else None,
            "date": date_str,
            "ticker": "NOG",
            "source": "combined",
            "annual_metrics": {
                "pe_ratio": pe_ratio,
                "roe": roe,
                "debt_to_equity": de_ratio,
                # "price_to_book": price_to_book,
                # "market_cap": market_cap
                }
            }
        }
        alldata.append(json_output)

with open('data/chunks/fin_chunks.json', 'w', encoding='utf-8') as f:
    json.dump(alldata, f, indent=4)

