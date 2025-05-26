import numpy as np 
from src.rl.agent import QLearningAgent

def test_q_learning_agent_action_and_update():
    agent = QLearningAgent(state_size=3, action_size=3, epsilon=0)
    state = np.array([100, 2, 0.5])
    next_state = np.array([102, 1.5, 0.7])

    # Initially no q-values - choose random or default action
    action = agent.get_action(state)
    assert action in [0, 1, 2]

    # Update Q-table with dummy reward
    agent.update_q_table(state, action, reward=10, next_state=next_state)
    state_key = tuple(np.round(state, 4))
    assert state_key in agent.q_table
    assert agent.q_table[state_key][action] != 0

    print('Agent action and update test passed!')

if __name__=='__main__':
    test_q_learning_agent_action_and_update()