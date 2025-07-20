import numpy as np 

def build_state(current_price, forecast_price, sentiment_score):
    """
    Create a state vector for the RL agent from the market data.
    Args:
        current_price (float): Current stocl price
        forecast_price (float): Forecasted price from the predictive model
        sentiment_score (float): Sentiment score from news
    Returns:
        np.array: state vector containing:
            - current_price
            - price difference (forecast_price - current_price)
            - sentiment_score 
    """
    delta = forecast_price - current_price
    return np.array([current_price, delta, sentiment_score])


