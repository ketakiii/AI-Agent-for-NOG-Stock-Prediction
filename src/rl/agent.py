import numpy as np 
import random

class QLearningAgent:
    def __init__(self, state_size, action_size=3, alpha=0.1, gamma=0.95, epsilon=0.1):
        """
        Q-learning agent initialize class.
        Args:

            state size (int): Dimension of the state vector
            action size (int): number of possible actions (3: Hold, Buy, Sell)
            alpha (float): learning rate
            gamma (float): discount factor
            epsilon (float): exploration rate for epsilon greedy policy
        """
        self.q_table = {}
        self.state_size = state_size
        self.action_size = action_size
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def get_action(self, state):
        """
        Choose an action based on the epsilon-greedy policy.
        Args: 
            state (np.array): current state vector
        Returns:
            int: Action index (0=Hold, 1=Buy, 2=Sell)
        """
        # convert state to tuple
        state_key = tuple(np.round(state, 4))
        # explore randomly with probability epsilon or if state not seen 
        if random.random() < self.epsilon or state_key not in self.q_table:
            return random.randint(0, self.action_size - 1)
        # otherwise exploit best known action
        return int(np.argmax(self.q_table[state_key]))

    def update_q_table(self, state, action, reward, next_state):
        """
        Update Q-values based on observed reward and next state.
        Args:
            state (np.array): previous state vector
            action (int): Action taken 
            reward (float): Reward received after action
            next_state (np.array): next state vector after action
        """
        state_key = tuple(np.round(state, 4))
        next_key = tuple(np.round(next_state, 4))

        # Initialize Q-values for states if unseen 
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_size)
        if next_key not in self.q_table:
            self.q_table[next_key] = np.zeros(self.action_size)

        # Calculate TD target and error
        best_next = np.max(self.q_table[next_key])
        td_target = reward + self.gamma * best_next
        td_error = td_target - self.q_table[state_key][action]

        # Update Q-value for (state, action)
        self.q_table[state_key][action] += self.alpha * td_error
    
    