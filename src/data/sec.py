import os
import requests
from bs4 import BeautifulSoup

# def download_sec_filings(cik, form_types, save_dir='')
url = f'https://financialmodelingprep.com/api/v3/income-statement/NOG?period=quarter&limit=4&apikey=gsYfmvJGR5z8Ezl4DR9t68F25Px8bsgR'
res = requests.get(url)
print(res.status_code)