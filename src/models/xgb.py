import sys
from src.data.data_pipeline import run_pipeline
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
import pickle
import os

def get_data():
    """
    Fetches and preprocess data from the data pipeline.
    """
    df = run_pipeline()
    features = df.drop(columns=['Date', 'Close'])
    target = df['Close']
    return features, target

def train_test_split_func():
    """
    Splits the data into training and testing sets.
    """
    features, target = get_data()
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def train_model(X_train, y_train, params=None):
    """
    Train XGBoost model.
    Args:
        X_train (pd.DataFrame): Training features.
        X_test (pd.DataFrame): Testing features.
        y_train (pd.Series): Training target.
        y_test (pd.Series): Testing target.
    Returns:
        xgb_model (XGBRegressor): Trained XGBoost model.
    """
    default_params = {
        "objective": "reg:squarederror",
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 5,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
    }
    if params:
        default_params.update(params)
    model = xgb.XGBRegressor(**default_params)
    model.fit(X_train, y_train)
    return model

def save_model(path='models/xgb_model.pkl'):
    """
    Save the trained model to a file.
    Args:
        model (XGBRegressor): Trained XGBoost model.
        path (str): Path to save the model.
    """
    X_train, X_test, y_train, y_test = train_test_split_func()
    model = train_model(X_train, y_train)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)

def load_model(path='models/xgb_model.pkl'):
    """
    Load the trained model from a file.
    Args:
        path (str): Path to the saved model.
    Returns:
        model (XGBRegressor): Loaded XGBoost model.
    """
    with open(path, "rb") as f:
        model = pickle.load(f)
    return model

if __name__ == "__main__":
    save_model()






