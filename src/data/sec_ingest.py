import os 
import requests
from datetime import datetime
import json
import time 

USER_AGENT = 'Ketaki ketaki.kolhatkar99@gmail.com'
TICKER = 'NOG'
FORMS = ['10-K', '10-Q']
YEARS = 2
JSONL_PATH = 'data/chunks/corpus.jsonl'

def get_cik(ticker):
    """
    Get the CIK number from the ticker.
    Args:
        ticker
    Returns:
        CIK number 
    """
    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    headers = {"User-Agent": USER_AGENT}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()
    with open('test.json', 'w') as f:
        json.dump(data, f, indent=4)
    exit(1)
    #     if v['ticker'].lower() == ticker.lower():
    #         return str(v['cik_str']).zfill(10)
    # raise ValueError(f"CIK for ticker {ticker} not found.")    

def fetch_submissions_json():
    """
    
    """
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def filter_filings(submissions_json, years):
    cutoff = datetime.now() - timedelta(days=365*years)
    indices = []
    for i, date_str in enumerate(submissions_json['filings']['recent']['filingDate']):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if date >= cutoff:
            indices.append(i)
    return indices


def download_filing_text(cik, accession_no):
    accession_nodash = accession_no.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_nodash}/{accession_no}.txt"
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text


def extract_snippet(filing_text, max_lines=10):
    # Extract first few non-empty lines as snippet
    lines = [line.strip() for line in filing_text.splitlines() if line.strip()]
    snippet = " ".join(lines[:max_lines])
    # Truncate if too long
    return snippet[:500] + ("..." if len(snippet) > 500 else "")


def create_jsonl_entry(ticker, form, filing_date, accession_no, snippet):
    entry = {
        "text": f"Filing type {form} submitted by {ticker} on {filing_date}. {snippet}",
        "metadata": {
            "type": "sec_filing",
            "form": form,
            "date": filing_date,
            "ticker": ticker,
            "accession_number": accession_no,
            "source": "sec.gov"
        }
    }
    return entry


def append_to_jsonl(entry, filepath):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# --- MAIN PROCESS ---

def main():
    cik = get_cik(TICKER)
    print(f"CIK for {TICKER}: {cik}")

    submissions_json = fetch_submissions_json(cik)
    recent_indices = filter_filings(submissions_json, YEARS)

    count = 0
    for i in recent_indices:
        form = submissions_json['filings']['recent']['form'][i]
        if form not in FORMS:
            continue
        accession_no = submissions_json['filings']['recent']['accessionNumber'][i]
        filing_date = submissions_json['filings']['recent']['filingDate'][i]

        print(f"Downloading {form} filing dated {filing_date}...")

        try:
            filing_text = download_filing_text(cik, accession_no)
            snippet = extract_snippet(filing_text)
            entry = create_jsonl_entry(TICKER, form, filing_date, accession_no, snippet)
            append_to_jsonl(entry, JSONL_PATH)
            count += 1
            # Be polite to SEC servers
            time.sleep(0.5)
        except Exception as e:
            print(f"Error downloading filing {accession_no}: {e}")

    print(f"Done. Appended {count} filings to {JSONL_PATH}")


if __name__ == "__main__":
    main()