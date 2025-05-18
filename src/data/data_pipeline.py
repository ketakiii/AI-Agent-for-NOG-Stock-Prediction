import datetime
from datetime import date
from src.features.feature_engineering import compute_technical_indicators, macroeconomic_indicators
import math
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import ta
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf

def get_data_from_yahoo(ticker, startdate, enddate):
    """
    Fetches historical stock data from Yahoo Finance.
    
    Args:
        ticker (str): The stock ticker symbol.
        startdate (str): The start date for fetching data.
        enddate (str): The end date for fetching data.

    Returns:
        pd.DataFrame: historical stock data.
    """
    df = yf.download(ticker, start=startdate, end=enddate)
    df = df.dropna().reset_index(drop=True)
    return df

def get_data_from_csv(filepath, startdate, enddate):
    """
    Read stock data from presaved CSV file
    Args:
        filepath (str): The path to the CSV file.
    Returns:
        pd.DataFrame: historical stock data.
    """
    df = pd.read_csv(filepath)

    df['Date'] = pd.to_datetime(df['Date'])
    df = df[(df['Date'] >= startdate) & (df['Date'] <= enddate)].reset_index(drop=True)
    df = df.dropna().reset_index(drop=True)
    return df

def preprocess_data(main_df, macro_df):
    """
    Preprocesses the data by fetching stock data, computing technical indicators, and merging with macroeconomic indicators.
    """
    # data = get_data_from_csv(filepath, starttime, endtime)
    tech_data = compute_technical_indicators(main_df).dropna()
    tech_data['Date'] = pd.to_datetime(tech_data['Date'])
    macro_df['Date'] = pd.to_datetime(macro_df['Date'])
    # Merge the two dataframes on the 'Date' column
    merged_data = pd.merge_asof(tech_data, macro_df, on='Date', direction='backward')
    merged_data.fillna(method='ffill', inplace=True)  # Forward fill any missing values
    merged_data.dropna(inplace=True)  # Drop any remaining NaN values
    return merged_data

def run_pipeline(ticker='NOG', startdate='2023-04-27', enddate='2025-04-30'):
    """
    Main func to run the data pipeline.
    Args:
        ticker (str): The stock ticker symbol.
        startdate (str): The start date for fetching data.
        enddate (str): The end date for fetching data.
    Returns:
        pd.DataFrame: Preprocessed data with technical and macroeconomic indicators.
    """
    # fetch stock data
    filepath = 'data/NOG_2012-01-01_2025-04-27.csv'
    stock_df = get_data_from_csv(filepath, startdate, enddate)
    macro_df = macroeconomic_indicators(startdate, enddate)
    processed_data = preprocess_data(stock_df, macro_df)
    return processed_data

if __name__ == "__main__":
    df = run_pipeline()
    print(df.shape)






