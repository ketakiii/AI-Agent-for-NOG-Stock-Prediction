import requests
import pandas as pd
import os

TICKER = "NOG"
API_KEY = os.getenv("FMP_API_KEY")

def generate_fundamentals_df():
    """
    Fetches financial ratios and key metric from Financial Modeling Prep API.
    Args:
        None
    Returns:
        pd.DataFrame: df containing financial ratios and key metric.
    """
    # --- Ratios endpoint ---
    ratios_url = f"https://financialmodelingprep.com/api/v3/ratios/{TICKER}?apikey={API_KEY}"
    ratios_response = requests.get(ratios_url).json()

    # --- Key metrics endpoint (to get missing P/E) ---
    key_metrics_url = f"https://financialmodelingprep.com/api/v3/key-metrics/{TICKER}?apikey={API_KEY}"
    key_metrics_response = requests.get(key_metrics_url).json()

    # Convert to DataFrames
    df_ratios = pd.DataFrame(ratios_response)
    df_key_metrics = pd.DataFrame(key_metrics_response)

    # Merge on date
    df = pd.merge(df_ratios, df_key_metrics[['date', 'peRatio']], on='date', how='left')

    # Rename and select relevant columns
    df = df[[
        'date',
        'peRatio',
        'priceToBookRatio',
        'returnOnEquity',
        'debtEquityRatio'
    ]]
    df.rename(columns={
        'date': 'Date',
        'peRatio': 'P/E Ratio',
        'priceToBookRatio': 'Price to Book',
        'returnOnEquity': 'ROE',
        'debtEquityRatio': 'Debt to Equity'
    }, inplace=True)

    # --- Profile endpoint for latest Market Cap ---
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{TICKER}?apikey={API_KEY}"
    profile_response = requests.get(profile_url).json()

    # Append static market cap to each row (historical not available from FMP)
    market_cap = profile_response[0].get('mktCap') if profile_response else None
    df['Market Cap (latest)'] = market_cap

    # Save or display
    df.to_csv("data/fundamentals.csv", index=False)


def generate_chunks():
    """
    Generates chunks of data for processing.
    """
    chunks = []
    df = pd.read_csv("data/fundamentals.csv")
    for _, row in df.iterrows():
        text = (
            f'As of {row["Date"]}, Northetern Oil & Gas Inc. (NOG) had a P/E Ratio of {row["P/E Ratio"]:.2f}, '
            f'a price to book ratio of {row["Price to Book"]:.2f}, return on equity of {row["ROE"]:.2f}, '
            f'and debt-to-equity ratio of {row["Debt to Equity"]:.2f}. The market capitalization was at that time was approximately'\
            f'{row["Market Cap"]:.2f}.'
        )
        chunks.append(text)
    data = pd.DataFrame(chunks, columns=['text'])
    data.to_csv("data/fundamentals_chunks.csv", index=False)

if __name__=='__main__':
    generate_chunks()
    print('Fundamentals chunks generated successfully!')