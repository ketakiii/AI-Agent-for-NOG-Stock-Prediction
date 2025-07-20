import requests
import os

def get_filing_urls(ticker, form_type, count=2):
    downloaded = 0
    base_url = "https://data.sec.gov/submissions/CIK{}.json"
    # You need to get the CIK for your ticker, example for NOG is '0001593095'
    cik = get_cik_from_ticker(ticker)
    url = base_url.format(cik.zfill(10))
    headers = {
        'User-Agent': 'Ketaki ketaki.kolhatkar99@gmail.com'
    }
    resp = requests.get(url, headers=headers)
    data = resp.json()
    filings = data['filings']['recent']

    urls = []
    for i, form in enumerate(filings['form']):
        if form == form_type:
            if downloaded >= count:
                break
            accession_no = filings['accessionNumber'][i].replace('-', '')
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_no}/{accession_no}-index.htm"
            urls.append(filing_url)
            downloaded += 1
    return urls

def get_cik_from_ticker(ticker):
    # You can maintain a dict or query this JSON mapping once and cache it:
    url = 'https://www.sec.gov/files/company_tickers.json'
    headers = {'User-Agent': 'Your Name your_email@example.com'}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    for item in data.values():
        if item['ticker'].lower() == ticker.lower():
            return str(item['cik_str'])
    raise ValueError("Ticker not found")

def download_filing(url, save_folder):
    headers = {'User-Agent': 'Ketaki ketaki.kolhatkar99@gmail.com'}
    resp = requests.get(url, headers=headers)
    os.makedirs(save_folder, exist_ok=True)
    filename = url.split('/')[-1]
    path = os.path.join(save_folder, filename)
    with open(path, 'wb') as f:
        f.write(resp.content)
    print(f"Saved filing to {path}")

# Usage example
ticker = "NOG"
form = "10-K"
save_folder = "./sec_filings/NOG/10-K"
os.makedirs(save_folder, exist_ok=True)
urls = get_filing_urls(ticker, form, count=2)

for url in urls:
    download_filing(url, save_folder)
