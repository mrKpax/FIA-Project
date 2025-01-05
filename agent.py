import random
from collections import defaultdict, deque
from typing import List
import pandas as pd

class ReplayBuffer:
    """Creates a circular buffer to store game experiences"""
    def __init__(self, capacity=10000):
        """Initialize replay buffer with max number of experiences to store (default 10000)"""
        self.buffer = deque(maxlen=capacity)
    
    def add(self, experience):
        """Adds a single experience tuple (state, action, reward, next_state) to buffer,
        once capacity is reached, oldest experiences are automatically removed"""
        self.buffer.append(experience)
    
    def sample(self, batch_size):
        """Randomly samples experiences for training.
        Returns experiences to avoid sampling issues with small buffers"""
        return random.sample(list(self.buffer), min(batch_size, len(self.buffer)))

class BlackjackRLAgent:
    """Reinforcement learning agent for playing blackjack"""
    def __init__(self, alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        """Initialize the RL agent with given parameters"""
        self.q_table = defaultdict(lambda: {'hit': 0.0, 'stay': 0.0}) # Maps state-action pairs to expected rewards using defaultdict
        self.alpha = alpha # Learning rate, controls how much new information overrides old
        self.gamma = gamma # Discount factor, values future rewards vs immediate ones
        self.epsilon = epsilon # Exploration rate, controls random vs learned actions
        self.epsilon_min = epsilon_min # Ensures some exploration
        self.epsilon_decay = epsilon_decay # Controls exploration reduction
        self.replay_buffer = ReplayBuffer()
        self.batch_size = 32 # Number of experiences to learn from at once (32)
        self.training_mode = False

    def train_from_csv(self, csv_file: str, epochs: int = 1):
        """Train the agent using historical data from a CSV file. Loads and processes historical game data validating CSV format or creating if missing, processes each row into experiences and trains for specified number of epochs decaying epsilon after each epoch"""
        print(f"Loading training data from {csv_file}...")
        try:
            df = pd.read_csv(csv_file)
            required_columns = ['Player Value', 'Dealer Card', 'Ace', 'Action', 'Reward']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Warning: Missing columns in training data: {', '.join(missing_columns)}")
                print("Expected columns: Player Value, Dealer Card, Ace, Action, Reward")
                print("Creating empty training file with correct columns...")
                
                # Create empty DataFrame with correct 
                empty_df = pd.DataFrame(columns=required_columns)
                empty_df.to_csv(csv_file, index=False)
                return
                
        except FileNotFoundError:
            print(f"Warning: {csv_file} not found. Creating new file with correct columns...")
            empty_df = pd.DataFrame(columns=['Player Value', 'Dealer Card', 'Ace', 'Action', 'Reward'])
            empty_df.to_csv(csv_file, index=False)
            return
        except pd.errors.EmptyDataError:
            print(f"Warning: {csv_file} is empty. Starting with empty Q-table.")
            return
        
        print(f"Training for {epochs} epochs on {len(df)} examples...")
        for epoch in range(epochs):
            for _, row in df.iterrows():
                try:
                    # Create state tuple from CSV data
                    state = (row['Player Value'], row['Dealer Card'], bool(row['Ace']))
                    action = row['Action'].lower()
                    
                    if action not in ['hit', 'stay']:
                        print(f"Warning: Invalid action '{action}' in training data. Skipping...")
                        continue
                        
                    reward = row['Reward']
                    if reward != 0: # Game ended
                        next_state = None
                    else:
                        # For continuing states, we can assume the next state from the next row
                        # But for simplicity, we'll use None here too
                        next_state = None
                    
                    # Add to replay buffer
                    self.replay_buffer.add((state, action, reward, next_state))
                    
                    # Learn from this experience
                    self.learn_from_replay()
                    
                except KeyError as e:
                    print(f"Warning: Error processing row: {e}")
                    continue

            # Decay epsilon after each epoch
            self.decay_epsilon()
            
            if (epoch + 1) % 10 == 0:
                print(f"Completed epoch {epoch + 1}/{epochs}")
        
        print("Training completed!")
        print(f"Q-table has {len(self.q_table)} states")
        
        print("\nExample Q-values:")
        sample_states = list(self.q_table.items())[:5]
        for state, actions in sample_states:
            print(f"State {state}: {actions}")
    
    def get_state(self, player_cards: List, dealer_upcard) -> tuple:
        """Converts game state into a tuple format for Q-learning"""
        player_sum = sum(card.get_value() for card in player_cards)
        dealer_value = dealer_upcard.get_value()
        usable_ace = any(card.value == 'A' for card in player_cards)
        # Adjust for aces
        if player_sum > 21 and usable_ace:
            player_sum -= 10
        return (player_sum, dealer_value, usable_ace)

    def choose_action(self, state: tuple) -> str:
        """Choose an action based on current state and exploration strategy. Uses epsilon-greedy strategy (random action with probability epsilon (exploration) or best known action with probability 1-epsilon (exploitation))"""
        if not self.training_mode:
            return max(self.q_table[state].items(), key=lambda x: x[1])[0] # Exploitation
        
        if random.random() < self.epsilon: 
            return random.choice(['hit', 'stay']) # Exploration
        return max(self.q_table[state].items(), key=lambda x: x[1])[0] # Exploitation

    def learn_from_replay(self):
        """Update Q-values using experiences from replay buffer. Samples batch of experiences and for each experience calculates max future Q-value and updates Q-value using formula Q(s,a) = Q(s,a) + α * (R + γ * max(Q(s')) - Q(s,a))"""
        if len(self.replay_buffer.buffer) < self.batch_size:
            return
            
        experiences = self.replay_buffer.sample(self.batch_size)
        for state, action, reward, next_state in experiences:
            next_max_q = 0 if next_state is None else max(self.q_table[next_state].values())
            old_q = self.q_table[state][action]
            new_q = old_q + self.alpha * (reward + self.gamma * next_max_q - old_q)
            self.q_table[state][action] = new_q

    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)