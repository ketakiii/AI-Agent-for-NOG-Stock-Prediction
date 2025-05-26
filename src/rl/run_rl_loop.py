from src.rl.agent import QLearningAgent
from src.rl.state_builder import build_state
from src.rl.reward import compute_reward

def simulate_trading(env, agent):
    """
    Simulate trading episodes in a given env using the RL agent.
    Args:
        env: environment with methods to current price, forecast, sentiment and step.
        agent (QLearningAgent): RL agent instance 
    """
    total_reward = 0
    # initialize state with current market info
    state = build_state(env.current_price(), env.forecast(), env.sentiment())

    for t in range(env.steps):
        # Agent selects action based on state
        action = agent.get_action(state)
        # env returns award and next state based on action
        reward, next_state = env.step(action)
        # Agent updates Q-table based on experience
        agent.update_q_table(state, action, reward, next_state)
        # Accumulate reward and move to next state
        total_reward += reward
        state = next_state
    return total_reward