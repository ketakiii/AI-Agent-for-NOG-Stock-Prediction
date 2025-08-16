import datetime
from datetime import date, timedelta, datetime as dt
from dateutil.relativedelta import relativedelta
from src.features.feature_engineering import compute_technical_indicators, macroeconomic_indicators
from src.data.news_ingest import run_news_data_pipeline
import math
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import ta
import warnings
import logging
warnings.filterwarnings("ignore")
import yfinance as yf
import os 

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

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
    logger.info(f"STARTING: get_data_from_yahoo")
    logger.info(f"Parameters: ticker={ticker}, startdate={startdate}, enddate={enddate}")
    
    try:
        logger.info(f"1: Calling yf.download for {ticker}...")
        logger.info(f"Fetching data from Yahoo Finance API...")
        
        df = yf.download(ticker, start=startdate, end=enddate)
        
        logger.info(f"COMPLETED: Yahoo Finance API call successful")
        logger.info(f"Raw data shape: {df.shape}")
        logger.info(f"Date range: {df.index.min()} to {df.index.max()}")
        logger.info(f"Columns: {list(df.columns)}")
        
        logger.info(f"Processing Yahoo Finance data...")
        df = process_data_from_yahoo(df)
        
        logger.info(f"COMPLETED: Data processing successful")
        logger.info(f"Processed data shape: {df.shape}")
        logger.info(f"Final columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        logger.error(f"EXCEPTION in get_data_from_yahoo: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {e}")
        raise

def process_data_from_yahoo(df):
    """
    Process the data fetched from Yahoo Finance.
    
    Args:
        df (pd.DataFrame): The stock data DataFrame.

    Returns:
        pd.DataFrame: processed stock data.
    """
    logger.info(f"STARTING: process_data_from_yahoo")
    logger.info(f"Input data shape: {df.shape}")
    
    try:
        logger.info(f"Processing column headers...")
        headers_as_rows = pd.DataFrame([df.columns.tolist()])
        cols = [col[0] for col in headers_as_rows.iloc[0].to_list()]
        df.columns = cols
        
        logger.info(f"COMPLETED: Column headers processed")
        logger.info(f"New columns: {list(df.columns)}")
        
        logger.info(f"Resetting index...")
        df.reset_index(inplace=True)
        
        logger.info(f"COMPLETED: Index reset")
        logger.info(f"Final data shape: {df.shape}")
        
        return df
        
    except Exception as e:
        logger.error(f"EXCEPTION in process_data_from_yahoo: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise

def get_data_from_csv(filepath, startdate, enddate):
    """
    Read stock data from presaved CSV file
    Args:
        filepath (str): The path to the CSV file.
    Returns:
        pd.DataFrame: historical stock data.
    """
    logger.info(f"STARTING: get_data_from_csv")
    logger.info(f"File path: {filepath}")
    logger.info(f"Date range: {startdate} to {enddate}")
    
    try:
        logger.info(f"Reading CSV file...")
        df = pd.read_csv(filepath)
        logger.info(f"COMPLETED: CSV file read successfully")
        logger.info(f"Raw data shape: {df.shape}")

        logger.info(f"Converting date column...")
        df['Date'] = pd.to_datetime(df['Date'], format='mixed')
        logger.info(f"COMPLETED: Date column converted")
        
        logger.info(f"Filtering by date range...")
        # Convert startdate and enddate to datetime for comparison
        startdate_dt = pd.to_datetime(startdate)
        enddate_dt = pd.to_datetime(enddate)
        df = df[(df['Date'] >= startdate_dt) & (df['Date'] <= enddate_dt)].reset_index(drop=True)
        logger.info(f"COMPLETED: Date filtering applied")
        logger.info(f"Filtered data shape: {df.shape}")
        
        logger.info(f"Cleaning data...")
        df = df.dropna().reset_index(drop=True)
        logger.info(f"COMPLETED: Data cleaning completed")
        logger.info(f"Final data shape: {df.shape}")

        return df
        
    except Exception as e:
        logger.error(f"EXCEPTION in get_data_from_csv: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise

def preprocess_data(main_df, macro_df):
    """
    Preprocesses the data by fetching stock data, computing technical indicators, and merging with macroeconomic indicators.
    """
    logger.info(f"STARTING: preprocess_data")
    logger.info(f"Main data shape: {main_df.shape}")
    logger.info(f"Macro data shape: {macro_df.shape}")
    
    try:
        logger.info(f"Computing technical indicators...")
        tech_data = compute_technical_indicators(main_df).dropna()
        logger.info(f"COMPLETED: Technical indicators computed")
        logger.info(f"Technical data shape: {tech_data.shape}")
        
        logger.info(f"Converting date columns...")
        tech_data['Date'] = pd.to_datetime(tech_data['Date'], format='mixed')
        macro_df['Date'] = pd.to_datetime(macro_df['Date'], format='mixed')
        logger.info(f"COMPLETED: Date columns converted")
        
        logger.info(f"Merging technical and macro data...")
        # Merge the two dataframes on the 'Date' column
        merged_data = pd.merge_asof(tech_data, macro_df, on='Date', direction='backward')
        logger.info(f"COMPLETED: Data merged")
        logger.info(f"Merged data shape: {merged_data.shape}")
        
        logger.info(f"Handling missing values...")
        merged_data.fillna(method='ffill', inplace=True)  # Forward fill any missing values
        merged_data.dropna(inplace=True)  # Drop any remaining NaN values
        logger.info(f"COMPLETED: Missing values handled")
        logger.info(f"Final data shape: {merged_data.shape}")
        
        return merged_data
        
    except Exception as e:
        logger.error(f"EXCEPTION in preprocess_data: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise

def run_data_pipeline(ticker='NOG', csvflag=True):
    """
    Main func to run the data pipeline.
    Args:
        ticker (str): The stock ticker symbol.
        csvflag (bool): If True, use existing CSV. If False, fetch fresh data from Yahoo Finance.
    Returns:
        pd.DataFrame: Preprocessed data with technical and macroeconomic indicators.
    """
    logger.info(f"STARTING: run_data_pipeline")
    logger.info(f"Parameters: ticker={ticker}, csvflag={csvflag}")
    logger.info(f"Data source: {'Existing CSV' if csvflag else 'Yahoo Finance API (fresh)'}")
    stock_csv_path = os.path.join(DATA_DIR, 'NOG.csv')
    try:
        logger.info(f"Reading base CSV file...")
        data = pd.read_csv(stock_csv_path)
        logger.info(f"COMPLETED: Base CSV read successfully")
        logger.info(f"Base data shape: {data.shape}")
        
        logger.info(f"Running news data pipeline...")
        run_news_data_pipeline()
        logger.info(f"COMPLETED: News data pipeline completed")
        
        if csvflag:
            logger.info(f"Using existing CSV data...")
            startdate = '2023-04-27'
            enddate = pd.to_datetime(data['Date'].iloc[-1]).date()
            logger.info(f"Date range: {startdate} to {enddate}")
            
            stock_df = get_data_from_csv(stock_csv_path, startdate, enddate)
            logger.info(f"COMPLETED: Existing CSV data loaded")
            logger.info(f" Stock data shape: {stock_df.shape}")
        else:
            logger.info(f"Fetching fresh data from Yahoo Finance...")
            today = datetime.date.today()
            startdate = (pd.to_datetime(data['Date'].iloc[-1]) + timedelta(days=1)).date()
            logger.info(f"Fetching data from {startdate} to {today}")
            
            try:
                # Fetch fresh data from Yahoo Finance
                df = get_data_from_yahoo(ticker, startdate, today)
                logger.info(f"COMPLETED: Fresh data fetched from Yahoo Finance")
                logger.info(f" Fresh data shape: {df.shape}")
                df['Date'] = pd.to_datetime(df['Date'], errors='ignore').dt.strftime('%Y-%m-%d')
                # Concatenate with existing data
                logger.info(f"Concatenating fresh data with existing data...")
                stock_df = pd.concat([data, df], ignore_index=True)
                stock_df = stock_df.drop_duplicates(subset=['Date']).reset_index(drop=True)
                logger.info(f"COMPLETED: Data concatenated successfully")
                logger.info(f"Combined data shape: {stock_df.shape}")
                
                # Update the CSV file with fresh data
                logger.info(f"Updating CSV file with fresh data...")
                stock_df.to_csv(stock_csv_path, index=False)
                logger.info(f"COMPLETED: CSV file updated with fresh data")
                
            except Exception as e:
                logger.error(f"FAILED to fetch fresh data from Yahoo Finance: {str(e)}")
                logger.warning(f"FALLBACK: Using existing CSV data instead...")
                
                startdate = '2023-04-27'
                enddate = pd.to_datetime(data['Date'].iloc[-1]).date()
                stock_df = get_data_from_csv(stock_csv_path, startdate, enddate)
                logger.info(f"FALLBACK COMPLETED: Using existing CSV data")
                logger.info(f"Stock data shape: {stock_df.shape}")
        
        logger.info(f"Computing macroeconomic indicators...")
        stock_df['Date'] = pd.to_datetime(stock_df['Date'])
        two_years_data = dt.now() - pd.DateOffset(years=2)
        stock_df = stock_df[stock_df['Date'] >= two_years_data]
        try:
            # Get date range for macroeconomic indicators
            startime = stock_df['Date'].min()
            endtime = stock_df['Date'].max()
            macro_df = macroeconomic_indicators(startime, endtime)
            logger.info(f"COMPLETED: Macro indicators computed")
            logger.info(f"Macro data shape: {macro_df.shape}")
        except Exception as e:
            logger.error(f"FAILED to compute macroeconomic indicators: {str(e)}")
            logger.warning(f"FALLBACK: Creating empty macro dataframe...")
            # Create empty macro dataframe as fallback
            macro_df = pd.DataFrame({'Date': stock_df['Date']})
            logger.info(f"FALLBACK COMPLETED: Empty macro dataframe created")
            logger.info(f"Macro data shape: {macro_df.shape}")
        
        logger.info(f"Preprocessing data...")
        try:
            final_data = preprocess_data(stock_df, macro_df)
            logger.info(f"COMPLETED: Data preprocessing completed")
            logger.info(f"Final data shape: {final_data.shape}")
        except Exception as e:
            logger.error(f"FAILED to preprocess data: {str(e)}")
            logger.warning(f"FALLBACK: Using stock data without macro indicators...")
            # Use stock data without macro indicators as fallback
            final_data = stock_df.copy()
            logger.info(f"FALLBACK COMPLETED: Using stock data without preprocessing")
            logger.info(f" Final data shape: {final_data.shape}")
        
        logger.info(f" SUCCESS: Data pipeline completed successfully!")
        logger.info(f" Data source used: {'Existing CSV' if csvflag else 'Yahoo Finance API'}")
        logger.info(f" Final dataset shape: {final_data.shape}")
        logger.info(f" Date range: {final_data['Date'].min()} to {final_data['Date'].max()}")
        
        return final_data
        
    except Exception as e:
        logger.error(f" EXCEPTION in run_data_pipeline: {str(e)}")
        logger.error(f" Exception type: {type(e).__name__}")
        logger.error(f" Exception details: {e}")
        raise
    
    finally:
        logger.info(f" COMPLETED: run_data_pipeline")

if __name__ == "__main__":
    df = run_data_pipeline(csvflag=False)
    # print(df.shape)






