from src.rl.reward import compute_reward

def test_compute_reward():
    prev = 100
    curr = 110

    buy_reward = compute_reward(prev, curr, 1)
    sell_reward = compute_reward(prev, curr, 2)
    hold_reward = compute_reward(prev, curr, 0)

    assert buy_reward == 10
    assert sell_reward == -10
    assert hold_reward == 0

    print('Reward function test passed!')

if __name__=='__main__':
    test_compute_reward()