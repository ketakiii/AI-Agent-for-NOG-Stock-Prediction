from sec_edgar_downloader import Downloader

dl = Downloader(download_dir='./data/sec_filings', email_address="ketaki.kolhatkar99@gmail.com")
dl.get("10-K", "NOG")

print("Download complete.")
