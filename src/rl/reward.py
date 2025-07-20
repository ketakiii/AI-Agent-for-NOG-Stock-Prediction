
def compute_reward(previous_price, current_price, action):
    """
    Compute reward for the RL agent based on the price movement and action.
    Args:
        previous_price: price before taking the action
        current_price: Price after taking the action
        action: Action taken (0=Hold, 1=Buy, 2=Sell)
    Returns: 
        float: Reward value 
            - Buy: profit if price increased
            - Sell: profit if price decreased
            - Hold: Zero reward
    """
    if action == 1:     # Buy
        return current_price - previous_price
    elif action == 2:   # Sell
        return previous_price - current_price
    else:               # Hold
        return 0.0