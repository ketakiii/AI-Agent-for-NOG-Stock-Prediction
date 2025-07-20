from src.rl.state_builder import build_state

def test_build_state():
    current_price = 100
    forecast_price = 105
    sentiment = 0.3

    state = build_state(current_price, forecast_price, sentiment)
    assert len(state) == 3
    assert state[0] == current_price
    assert state[1] == forecast_price - current_price
    assert state[2] == sentiment

    print('State builder test passed!')

if __name__=='__main__':
    test_build_state()