import random
import numpy as np
import pandas as pd
from collections import defaultdict

# changable variables for Monte Carlo Algoritm
alpha = 0.1 # alpha value for learning tax
gamma = 1 # gamma value for future rewards
epsilon = 0.1 # epsilon value for exploration
action_space = [0,1] # AI's action, 0 stay / 1 hit

# Card Class
class Card:
    heart = "\u2665"
    spade = "\u2660"
    diamond = "\u2666"
    club = "\u2663"

    suits = {
        "diamonds": diamond,
        "hearts": heart,
        "spades": spade,
        "clubs": club
    }

    def __init__(self, suit, number):
        self.suit = suit
        self.number = number
        self.value = None

        if self.number in ['J', 'Q', 'K']:
            self.value = 10
        elif self.number == 'A':
            self.value = 11
        else:
            self.value = int(number)

    def __str__(self):
        """String representation of a card."""
        return f"{self.number}{Card.suits[self.suit]}"

    def format_cards(cards):
        """Formats a list of Card objects into a readable string"""
        return " ".join(str(card) for card in cards)

class Deck:
    def __init__(self):
        self.deck = self.generate_deck()
    
    @staticmethod
    def generate_deck():
        """Generates a shuffled deck with the specified number of decks."""
        numbers = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        deck = []

        deck = [
            Card(suit, number)
            for _ in range(5) #6 decks
            for number in numbers
            for suit in suits
        ]
        
        random.shuffle(deck)
        return deck

    def deal_card(self):
        return self.deck.pop(0)

    def shuffle_if_needed(self):
        cards_used = (6 * 52) - len(self.deck)
        if cards_used >= (6 * 52) // 2: # after about 3 decks
            self.deck = self.generate_deck()
            random.shuffle(self.deck)
            print("Deck reshuffled.")
            return True
        return False

def check_ace(hand): # true if ace is usable as 11
    ace = False
    result = sum(card.value for card in hand)
    for card in hand:
        if card.number == 'A':
            ace = True
    if ace and result - 1 + 11 <= 21:
        return True
    return False

def hand_value(hand): # calculate hand's value
    result = sum(card.value for card in hand)
    aces = sum(1 for card in hand if card.number == 'A')

    while result > 21 and aces:
        result -= 10
        aces -= 1

    return result

def is_blackjack(hand):
    """Check if the hand is a Blackjack"""
    return len(hand) == 2 and hand_value(hand) == 21


def game_result(dealer, player_hand, dealer_hand):
    pvalue = hand_value(player_hand)
    dvalue = hand_value(dealer_hand)

    player_bj = is_blackjack(player_hand)
    dealer_bj = is_blackjack(dealer_hand)

    if player_bj and dealer_bj:
        return True, None  # both bj, tie
    if player_bj and not dealer_bj:
        return True, True  # player wins with bj
    if dealer_bj:
        return True, False  # dealer wins with bj
    if pvalue > 21:
        return True, False # game over, dealer wins
    if pvalue == 21:
        return True, True # player wins
    if dvalue == 21:
        return True, False
    if not dealer:
        return False, False
    if dealer and pvalue <= 21 and dvalue > 21:
        return True, True  # player wins
    if dealer and pvalue > dvalue:
        return True, True
    if dealer and dvalue > pvalue:
        return True, False
    if dealer and dvalue == pvalue:
        return True, None  # tie
    return False, False

##### AI SECTION
def create_state_values(player_hand, dealer_hand):
    """Generate current state's values"""
    return hand_value(player_hand), hand_value(dealer_hand[:1]), check_ace(player_hand)

def set_q(Q, current_episode, gamma, alpha):
    for t in range(len(current_episode)): # "time" to analyze state-action-reward
        rewards = current_episode[t:, 2] # extract rewards from time "t"
        discount_rate = [gamma ** i for i in range(1, len(rewards) + 1)] # reduce importance of far rewards
        updated_reward = rewards * discount_rate # calculate future discount rewards
        Gt = np.sum(updated_reward) # sum of future rewards
        Q[current_episode[t][0]][current_episode[t][1]] += alpha * (Gt - Q[current_episode[t][0]][current_episode[t][1]]) # update Q(a,t) value
    return Q

def load_training_data(log_file):
    """Load data from CSV and turn them into episodes for training. Return an episode's list [(state, action, reward)]"""
    data = pd.read_csv(log_file)
    episodes = []

    for _, row in data.iterrows():
        state = (row['Player Value'], row['Dealer Card'], bool(row['Ace'])) # extract state
        action = 0 if row['Action'] == 'stay' else 1 # extract action (0 stay, 1 hit)
        reward = row['Reward'] # extract reward

        episodes.append((state, action, reward))

    return episodes

def update_q_from_csv(Q, training_data, gamma, alpha):
    """Update Q-function using episodes from training dataset"""
    for episode in training_data:
        state, action, reward = episode
        Gt = reward # actual reward is considered the return value
        Q[state][action] += alpha * (Gt - Q[state][action])  # update Q(s, a)

    return Q

def gen_action(state, epsilon, Q):
    prob_hit = Q[state][1]
    prob_stay = Q[state][0]

    if prob_hit > prob_stay:
        probs = [epsilon, 1 - epsilon]
    elif prob_stay > prob_hit:
        probs = [1 - epsilon, epsilon]
    else:
        probs = [0.5, 0.5]
    action = np.random.choice(np.arange(2), p=probs)
    return action

##### END AI SECTION

def main():
    AI = input("Vuoi abilitare l'AI? (s/n): ").lower() == "s"
    running = True
    wins = losses = draws = games = 0
    Q = defaultdict(lambda: np.zeros(2)) # dict of state-action couples
    current_episode = [] # sequence of state, action, reward
    deck = Deck()

    # Load training data from CSV
    training_file = "game_log.csv"
    training_data = load_training_data(training_file)
    Q = update_q_from_csv(Q, training_data, gamma, alpha)

    # Simulated rounds for AI
    simulated_rounds = 100000 if AI else None  # n. of rounds to simulate if AI is enabled
    ai_round_count = 0  # Counter for AI rounds  

    while running:
        if simulated_rounds and ai_round_count >= simulated_rounds:
            break  # Stop simulation after the desired number of rounds

        print(f"\n==================== NEW ROUND ====================")

        dealer_hand = [deck.deal_card(), deck.deal_card()]
        player_hand = [deck.deal_card(), deck.deal_card()]
        game_over = False
        dealer_turn = False

        while not game_over:
            print("\nDealer's cards:", Card.format_cards(dealer_hand[:1]), "[?]")
            print("Player's cards:", Card.format_cards(player_hand), "=>", hand_value(player_hand))

            if AI:
                current_state = create_state_values(player_hand, dealer_hand)
                action = gen_action(current_state, epsilon, Q)
                if action == 1: # hit
                    player_hand.append(deck.deal_card())
                else: # stay
                    dealer_turn = True
            else:
                action = input("\nDo you want hit or stay [h/s]?").lower()
                if action == "h":
                    player_hand.append(deck.deal_card())
                elif action == "s":
                    dealer_turn = True
                else:
                    print("Invalid action. Please type [h/s].")

            game_over, winner = game_result(dealer_turn, player_hand, dealer_hand)

            if dealer_turn:
                while hand_value(dealer_hand) < 17: # dealer stay on 17
                    dealer_hand.append(deck.deal_card())
                game_over, winner = game_result(dealer_turn, player_hand, dealer_hand)

        print(f"\n==================== NEW ROUND ====================")
        print("Dealer's cards:", Card.format_cards(dealer_hand), "=>", hand_value(dealer_hand))
        print("Player's cards:", Card.format_cards(player_hand), "=>", hand_value(player_hand))

        if winner is None:
            print("\nTie!")
            draws += 1
        elif winner:
            if is_blackjack(player_hand):
                print("\nPlayer wins with a Blackjack!")
            else:
                print("\nPlayer wins!")
            wins += 1
        else:
            print("\nDealer wins!")
            losses += 1

        games += 1

        print(f"Games: {games}, Wins: {wins}, Losses: {losses}, Draws: {draws}")
        win_per = (wins * 100)/games
        print(f"Wins percentage: {win_per:.2f}")

        deck.shuffle_if_needed()

        if not AI:
            play_again = input("\nDo you want to play another round [y/n]?: ").strip().lower()
            if play_again != "y":
                running = False
        else:
            current_episode = np.array(current_episode)
            Q = set_q(Q, current_episode, gamma, alpha)
            current_episode = []
            ai_round_count += 1  # Increment the AI round counter

if __name__ == "__main__":
    main()