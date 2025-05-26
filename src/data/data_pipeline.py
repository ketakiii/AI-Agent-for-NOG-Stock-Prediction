import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from src.features.feature_engineering import compute_technical_indicators, macroeconomic_indicators, classify_news_sentiment
from src.data.news_ingest import run_news_data_pipeline
import math
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import ta
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf

sentiment_map = {'Positive': 1, 'Neutral': 0, 'Negative': -1}

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
    df = process_data_from_yahoo(df)
    return df

def process_data_from_yahoo(df):
    """
    Process the data fetched from Yahoo Finance.
    
    Args:
        df (pd.DataFrame): The stock data DataFrame.

    Returns:
        pd.DataFrame: processed stock data.
    """
    headers_as_rows = pd.DataFrame([df.columns.tolist()])
    cols = [col[0] for col in headers_as_rows.iloc[0].to_list()]
    df.columns = cols
    df.reset_index(inplace=True)
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

def run_data_pipeline(ticker='NOG', csvflag=True):
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
    data = pd.read_csv('data/NOG.csv')
    run_news_data_pipeline()
    if csvflag:
        startdate = '2023-04-27'
        enddate = datetime.datetime.strptime(data['Date'].iloc[-1], '%Y-%m-%d')
        stock_df = get_data_from_csv('data/NOG.csv', startdate, enddate)
    else:
        today = datetime.date.today()
        startdate = (datetime.datetime.strptime(data['Date'].iloc[-1], '%Y-%m-%d') + timedelta(days=1)).date()
        enddate = today
        df = get_data_from_yahoo(ticker, startdate, enddate)
        stock_df = pd.concat([data, df])
        stock_df.to_csv('data/NOG.csv', index=False, encoding='utf-8-sig', sep=',', columns=['Date','Close','High','Low','Open','Volume'])
    macro_df = macroeconomic_indicators(startdate, enddate)
    processed_data = preprocess_data(stock_df, macro_df)
    return processed_data

if __name__ == "__main__":
    df = run_data_pipeline(csvflag=False)
    # print(df.shape)






