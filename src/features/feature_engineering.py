import pandas as pd
import numpy as np 
import pandas_datareader.data as web
import ta
import warnings
warnings.filterwarnings("ignore")
# OpenAI client removed since classify_news_sentiment is not used
from openai import OpenAI
from dotenv import load_dotenv
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def compute_technical_indicators(df):
    """
    Computes technical indicators for stock data.
    Args:
        df (pd.DataFrame): stock dataframe.
    Returns:
        pd.DataFrame: dataframe with technical indicators.
    """
    # Calculate moving averages
    df['ma_10'] = pd.DataFrame(df['Close'].rolling(window=10).mean())
    df['m_50'] = pd.DataFrame(df['Close'].rolling(window=50).mean())
    # daily change
    df['daily_change'] = df['Close'].pct_change()
    # volatility
    df['volatility_10'] = df['Close'].rolling(window=10).std()
    # RSI 
    df['RSI_14'] = calculate_rsi(df['Close'], window=14)
    # Bollinger Bands
    bb_indicator = ta.volatility.BollingerBands(close=df['Close'], window=20)
    df['bb_high'] = bb_indicator.bollinger_hband()
    df['bb_low'] = bb_indicator.bollinger_lband()
    # Momentum
    df['Momentum_10'] = df['Close'] - df['Close'].shift(10)  
    # Volume-Weighted Average Price (VWAP) = (Cumulative Sum of (Price * Volume)) / (Cumulative Sum of Volume)
    df['Cumulative_Price_Volume'] = (df['Close'] * df['Volume']).cumsum()
    df['Cumulative_Volume'] = df['Volume'].cumsum()
    df['VWAP'] = df['Cumulative_Price_Volume'] / df['Cumulative_Volume']
    return df

def calculate_rsi(series, window=14):
    """
    Calculate the Relative Strength Index for a series. 
    Args:
        series: pd.Series: The series to calculate RSI for
        window: int: The window size for RSI calculation
    Returns:
        pd.Series: The RSI values
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macroeconomic_indicators(startime, endtime):
    """
    Fetches macroenomic indicators - 
        FRED’s series "DCOILWTICO" provides the daily spot price of West Texas Intermediate (WTI) crude oil
    Args:
        df (pd.DataFrame): stock dataframe.
        startime (str): The start date for fetching data.
        endtime (str): The end date for fetching data.
    Returns:
        pd.DataFrame: dataframe with macroeconomic indicators.
    """
    oil_prices = fetch_oil_prices(startime, endtime)
    fed_funds = fetch_fed_funds(startime, endtime)
    macro_data = pd.merge_asof(oil_prices, fed_funds, on='Date', direction='backward')
    macro_data.fillna(method='ffill', inplace=True) # Forward fill any missing values
    macro_data.dropna(inplace=True) 
    return macro_data
    
def fetch_oil_prices(starttime, endtime):
    """
    Fetches oil prices from Yahoo Finance.
    Returns:
        pd.DataFrame: Oil prices data.
    """
    oil_prices = web.DataReader('DCOILWTICO', 'fred', starttime, endtime)
    oil_prices.reset_index(inplace=True)
    oil_prices.rename(columns={'DATE': 'Date', 'DCOILWTICO': 'Crude_Oil'}, inplace=True)
    oil_prices['Date'] = pd.to_datetime(oil_prices['Date'], format='mixed')
    oil_prices.sort_values('Date', inplace=True)
    return oil_prices

def fetch_fed_funds(starttime, endtime):
    """
    Fetches Federal Funds Rate data from Yahoo Finance.
    Returns:
        pd.DataFrame: Federal Funds Rate data.
    """
    fed_funds = web.DataReader('FEDFUNDS', 'fred', starttime, endtime)
    fed_funds.reset_index(inplace=True)
    fed_funds.rename(columns={'DATE': 'Date', 'FEDFUNDS': 'Fed_Funds_Rate'}, inplace=True)
    fed_funds['Date'] = pd.to_datetime(fed_funds['Date'], format='mixed')
    fed_funds.sort_values('Date', inplace=True)
    return fed_funds


