import pygame
import random
import sys
import os
from typing import List
from agent import BlackjackRLAgent

# Initialize Pygame and set up resource paths
pygame.init()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(SCRIPT_DIR, 'cards')

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
CARD_WIDTH = 100
CARD_HEIGHT = 150
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40

# Colors
WHITE = (252, 246, 245)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
RED = (220, 20, 60)
BLACKCHART = (16, 24, 32)

# Create window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Blackjack")
clock = pygame.time.Clock()

class Card:
    """Represents a playing card with suit, value and visual representation"""
    def __init__(self, suit: str, value: str):
        self.suit = suit
        self.value = value
        self.hidden = False
        try:
            self.image = self.load_image()
            self.back_image = pygame.image.load(os.path.join(CARDS_DIR, 'back.png'))
            # Scale images
            self.image = pygame.transform.scale(self.image, (CARD_WIDTH, CARD_HEIGHT))
            self.back_image = pygame.transform.scale(self.back_image, (CARD_WIDTH, CARD_HEIGHT))
        except pygame.error as e:
            print(f"Error loading card images: {e}")
            sys.exit(1)

    def load_image(self) -> pygame.Surface:
        """Load and return the card's image from file"""
        value_map = {
            'A': 'ace', 'K': 'king', 'Q': 'queen', 'J': 'jack',
            '10': '10', '9': '9', '8': '8', '7': '7', '6': '6',
            '5': '5', '4': '4', '3': '3', '2': '2'
        }
        suit_map = {
            '♠': 'spades', '♣': 'clubs', '♥': 'hearts', '♦': 'diamonds'
        }
        
        filename = f"{value_map[self.value]}_of_{suit_map[self.suit]}.png"
        return pygame.image.load(os.path.join(CARDS_DIR, filename))

    def get_value(self) -> int:
        """Return the numerical value of the card"""
        if self.value in ['J', 'Q', 'K']:
            return 10
        elif self.value == 'A':
            return 11  # Base value, will be adjusted in hand calculation
        return int(self.value)

    def __str__(self):
        """Returns a string representation of the card"""
        return f"{self.value}{self.suit}"

class Deck:
    """Represents a deck of playing cards"""
    def __init__(self):
        """Initialize a new shuffled deck"""
        self.cards = []
        self.init_deck()
        self.reshuffle_warning = False

    def init_deck(self):
        """Initialize and shuffle a new deck of cards"""
        suits = ['♠', '♣', '♥', '♦']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        self.cards = [Card(suit, value) for suit in suits for value in values]
        random.shuffle(self.cards)
        self.reshuffle_warning = False

    def draw(self) -> Card:
        """Draw and return the top card from the deck"""
        if len(self.cards) <= 156:  # About 3 decks
            self.reshuffle_warning = True
        return self.cards.pop()

class Button:
    """Represents a clickable button in the UI"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        """Initialize a button with position, size and text."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.visible = True
        self.enabled = True

    def draw(self, surface):
        """Draw the button on the given surface"""
        if not self.visible:
            return
        color = WHITE if self.enabled else (100, 100, 100)
        border_radius = min(self.rect.width, self.rect.height) // 4
        pygame.draw.rect(surface, color, self.rect, border_radius=border_radius)
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, GREEN)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class WinRateChart:
    """Represents a chart showing win rate statistics"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.win_rates = []
        self.games = []
        self.max_rate = 0
        
    def update(self, total_games, total_wins):
        """Update chart with new game statistics"""
        if total_games == 0:
            return
            
        win_rate = (total_wins / total_games) * 100
        self.max_rate = max(self.max_rate, win_rate)
        
        self.games.append(total_games)
        self.win_rates.append(win_rate)
    
    def draw(self, surface):
        # Draw chart background
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, BLACKCHART, (self.x, self.y, self.width, self.height), 2)

        # Calculate y-axis scale based on max rate
        y_scale = min(100, ((self.max_rate // 25) + 1) * 25)
        
        # Draw grid
        for i in range(5):
            y_pos = self.y + (i * self.height // 4)
            pygame.draw.line(surface, BLACKCHART, (self.x, y_pos), 
                           (self.x + self.width, y_pos), 1)
            value = y_scale - (i * y_scale/4)
            font = pygame.font.Font(None, 20)
            text = font.render(f"{value}%", True, BLACK)
            surface.blit(text, (self.x - 45, y_pos - 10))

        if len(self.games) > 0:
            max_games = self.games[-1]
            for i in range(0, max_games + 1, max(1, max_games // 4)):
                x_pos = self.x + (i / max_games) * self.width
                font = pygame.font.Font(None, 20)
                text = font.render(str(i), True, BLACK)
                surface.blit(text, (x_pos - text.get_width()//2, self.y + self.height + 5))
            
        if len(self.win_rates) < 2:
            return
            
        # Draw win rate line
        points = []
        # Scale based on max games number for x and win rate for y
        max_games = self.games[-1]
        for i in range(len(self.win_rates)):
            x = self.x + (self.games[i] / max_games) * self.width
            y = self.y + self.height - (self.win_rates[i] * self.height / y_scale)
            points.append((x, y))
            
        pygame.draw.lines(surface, RED, False, points, 3)
        
        # Draw latest stats
        font = pygame.font.Font(None, 40)
        latest_rate = self.win_rates[-1]
        stats = f"Win Rate: {latest_rate:.1f}%"
        text = font.render(stats, True, WHITE)
        surface.blit(text, (self.x + 90, self.y - 30))

class Game:
    """Main game class handling game logic and UI"""
    def __init__(self):
        """Initialize the game state and UI elements"""
        self.init_game()
        self.create_buttons()
        self.total_games = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_draws = 0
        self.hit_count = 0
        self.stand_count = 0
        self.ai_speed = 0  # 0 = normal, 1 = fast
        self.is_stopped = False

        self.chart = WinRateChart(WINDOW_WIDTH // 8, 300, 400, 200)

        self.agent.train_from_csv('game_log.csv', epochs=50)

    def init_game(self):
        """Initialize or reset game state"""
        self.deck = Deck()
        self.player_cards = []
        self.dealer_cards = []
        self.game_state = "waiting"
        self.current_winner = ""
        self.agent = BlackjackRLAgent()
        self.game_count = 0
        self.agent_playing = False
        self.warning_message = ""
        self.warning_timer = 0
        self.round_log = []  # Add this line to store round logs

    def create_buttons(self):
        """Create and initialize UI buttons"""
        button_y = WINDOW_HEIGHT - 50
        self.start_button = Button(WINDOW_WIDTH//2 + 80, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start")
        self.hit_button = Button(WINDOW_WIDTH//2 + 80, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Hit")
        self.stay_button = Button(WINDOW_WIDTH//2 + 300, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Stay")
        self.ai_button = Button(WINDOW_WIDTH//2 + 300, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "AI Play")
        self.stop_button = Button(WINDOW_WIDTH//2 + 300, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Stop")
        self.speed_button = Button(WINDOW_WIDTH//2 + 80, button_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Normal")

        self.hit_button.visible = False
        self.stay_button.visible = False
        self.stop_button.visible = False
        self.ai_button.visible = True
        self.speed_button.visible = False

    def log_game_state(self, message: str = None):
        """Logs the current game state to the console"""
        if message == "NEW ROUND":
            print("\n" + "=" * 20 + " NEW ROUND " + "=" * 20)
            
            # Log dealer's initial cards (one hidden)
            dealer_cards = [str(self.dealer_cards[0])] + ["[?]"]
            print(f"Dealer's cards: {' '.join(dealer_cards)}")
            
            # Log player's initial cards
            player_cards = [str(card) for card in self.player_cards]
            player_total = self.calculate_hand(self.player_cards)
            print(f"Player's cards: {' '.join(player_cards)} => {player_total}")
            
        elif message == "PLAYER HITS":
            player_cards = [str(card) for card in self.player_cards]
            player_total = self.calculate_hand(self.player_cards)
            print(f"Player's cards: {' '.join(player_cards)} => {player_total}")
            
        elif message == "DEALER REVEALS":
            dealer_cards = [str(card) for card in self.dealer_cards]
            dealer_total = self.calculate_hand(self.dealer_cards)
            print(f"Dealer's cards: {' '.join(dealer_cards)} => {dealer_total}")
            
        elif message == "GAME OVER":
            print("=" * 20 + " GAME OVER " + "=" * 20)
            print(f"{self.current_winner}")
            print(f"Epsilon: {self.agent.epsilon}")
            
            # Print overall statistics
            win_percentage = (self.total_wins / self.total_games * 100) if self.total_games > 0 else 0
            print(f"Games: {self.total_games}, Wins: {self.total_wins}, "
                  f"Losses: {self.total_losses}, Draws: {self.total_draws}")
            print(f"Wins percentage: {win_percentage:.2f}\n")

    def reset_game(self):
        self.deck = Deck()
        self.player_cards = []
        self.dealer_cards = []
        self.game_state = "playing"
        self.current_winner = ""
        self.hit_button.visible = True
        self.stay_button.visible = True
        self.start_button.visible = False
        self.ai_button.visible = False
        self.deal_initial_cards()
        self.log_game_state("NEW ROUND")

    def deal_initial_cards(self):
        """Deal the round's initial cards"""
        self.player_cards = [self.deck.draw(), self.deck.draw()]
        self.dealer_cards = [self.deck.draw(), self.deck.draw()]
        self.dealer_cards[0].hidden = True

    def calculate_hand(self, cards: List[Card]) -> int:
        """Calculate the hand value"""
        total = 0
        aces = sum(1 for card in cards if not card.hidden and card.value == 'A')
        
        # First sum all non-ace cards
        for card in cards:
            if not card.hidden and card.value != 'A':
                total += card.get_value()
        
        # Then handle aces
        for _ in range(aces):
            if total + 11 <= 21:
                total += 11
            else:
                total += 1
                
        return total

    def dealer_play(self):
        """Dealer's turn"""
        self.dealer_cards[0].hidden = False
        while self.calculate_hand(self.dealer_cards) < 17:
            self.dealer_cards.append(self.deck.draw())

    def determine_winner(self) -> str:
        """Determine winner of the round"""
        player_value = self.calculate_hand(self.player_cards)
        dealer_value = self.calculate_hand(self.dealer_cards)
        
        if player_value > 21:
            return "Dealer wins!"
        elif dealer_value > 21:
            return "Player wins!"
        elif player_value > dealer_value:
            return "Player wins!"
        elif dealer_value > player_value:
            return "Dealer wins!"
        return "Tie!"

    def draw_cards(self, cards: List[Card], y_pos: int):
        for i, card in enumerate(cards):
            x_pos = (WINDOW_WIDTH//2 + 250 - (len(cards) * CARD_WIDTH)//2) + i * (CARD_WIDTH + 10)
            screen.blit(card.back_image if card.hidden else card.image, (x_pos, y_pos))

    def handle_game_over(self, is_player_turn: bool = True):
        """Handles game over state and updates statistics"""
        self.game_count += 1
        self.total_games += 1
        
        if "Player wins" in self.current_winner:
            self.total_wins += 1
        elif "Dealer wins" in self.current_winner:
            self.total_losses += 1
        elif "Tie" in self.current_winner:
            self.total_draws += 1
            
        self.game_state = "game_over"
        self.log_game_state("DEALER REVEALS")
        self.log_game_state("GAME OVER")

        # Update chart
        if self.agent_playing:
            self.chart.update(self.total_games, self.total_wins)

        # Immediate reset in fast modes
        if self.agent_playing and self.ai_speed > 0:
            self.reset_game()
            return
            
        if self.agent_playing:
            pygame.time.set_timer(pygame.USEREVENT, 1000)

    def handle_ai_turn(self):
        """Handle AI's turn"""
        if self.game_state == "playing" and self.agent_playing:
            state = self.agent.get_state(self.player_cards, self.dealer_cards[1])
            action = self.agent.choose_action(state)
            
            if action == 'hit':
                self.hit_count += 1
                new_card = self.deck.draw()
                self.player_cards.append(new_card)
                self.log_game_state("PLAYER HITS")
                
                if self.calculate_hand(self.player_cards) > 21:
                    self.dealer_cards[0].hidden = False
                    self.game_state = "game_over"
                    self.current_winner = self.determine_winner()
                    reward = -1
                    next_state = None
                    self.handle_game_over(is_player_turn=False)
                    self.agent.decay_epsilon()
                else:
                    reward = 0
                    next_state = self.agent.get_state(self.player_cards, self.dealer_cards[1])
            else:  # stand
                self.stand_count += 1
                self.dealer_play()
                self.game_state = "game_over"
                self.current_winner = self.determine_winner()
                self.handle_game_over(is_player_turn=False)
                self.agent.decay_epsilon()
                
                if "Player wins" in self.current_winner:
                    reward = 1
                elif "Dealer wins" in self.current_winner:
                    reward = -1
                else:
                    reward = 0
                next_state = None
            
            self.agent.replay_buffer.add((state, action, reward, next_state))
            self.agent.learn_from_replay()
            
            if self.game_state == "game_over":
                self.agent.decay_epsilon()

    def run(self):
        """Handle round's game logic"""
        running = True
        while running:

            if self.agent_playing and not self.is_stopped:
                self.hit_button.visible = False
                self.stay_button.visible = False
                self.speed_button.visible = True
                self.handle_ai_turn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.USEREVENT:
                    if self.game_state == "game_over" and self.agent_playing and not self.is_stopped:
                        pygame.time.set_timer(pygame.USEREVENT, 0)
                        self.reset_game()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.speed_button.visible and self.speed_button.rect.collidepoint(mouse_pos):
                        self.ai_speed = (self.ai_speed + 1) % 2
                        if self.ai_speed == 0:
                            self.speed_button.text = "Normal"
                        elif self.ai_speed == 1:
                            self.speed_button.text = "Fast"
                    
                    elif self.start_button.visible and self.start_button.rect.collidepoint(mouse_pos):
                        self.reset_game()
                        self.deal_initial_cards()
                    
                    elif self.ai_button.visible and self.ai_button.rect.collidepoint(mouse_pos):
                        self.agent_playing = not self.agent_playing
                        self.ai_button.text = "Stop AI" if self.agent_playing else "AI Play"
                        self.stop_button.visible = self.agent_playing
                        self.is_stopped = False
                        if self.agent_playing:
                            self.reset_game()
                            self.deal_initial_cards()

                    elif self.stop_button.visible and self.stop_button.rect.collidepoint(mouse_pos):
                        self.is_stopped = not self.is_stopped
                        self.stop_button.text = "Resume" if self.is_stopped else "Stop"
                    
                    elif self.hit_button.visible and self.hit_button.rect.collidepoint(mouse_pos):
                        if self.game_state == "playing":
                            self.player_cards.append(self.deck.draw())
                            self.log_game_state("PLAYER HITS")
                            
                            if self.calculate_hand(self.player_cards) > 21:
                                self.dealer_cards[0].hidden = False
                                self.current_winner = self.determine_winner()
                                self.handle_game_over()
                    
                    elif self.stay_button.visible and self.stay_button.rect.collidepoint(mouse_pos):
                        if self.game_state == "playing":
                            self.dealer_play()
                            self.current_winner = self.determine_winner()
                            self.handle_game_over()

            # Draw
            screen.fill(GREEN)

            self.chart.draw(screen)
                
            # Draw stats
            font = pygame.font.Font(None, 45)
            stats_games = font.render(f"Games: {self.game_count}", True, WHITE)
            stats_games_rect = stats_games.get_rect(center=(WINDOW_WIDTH // 4, 100))
            screen.blit(stats_games, stats_games_rect)

            stats_wins = font.render(f"Wins: {self.total_wins}", True, WHITE)
            stats_wins_rect = stats_wins.get_rect(center=(WINDOW_WIDTH // 4, 130))
            screen.blit(stats_wins, stats_wins_rect)

            if self.agent_playing:
                font = pygame.font.Font(None, 36)

                epsilon_text = font.render(f"Epsilon: {self.agent.epsilon:.3f}", True, WHITE)
                epsilon_text_rect = epsilon_text.get_rect(center=(WINDOW_WIDTH // 4, 160))
                screen.blit(epsilon_text, epsilon_text_rect)

                action_text = font.render(f"Hits: {self.hit_count} | Stands: {self.stand_count}", True, WHITE)
                action_text_rect = action_text.get_rect(center=(WINDOW_WIDTH // 4 + 10, WINDOW_HEIGHT // 2 + 150))
                screen.blit(action_text, action_text_rect)

                #stands_text = font.render(f"Stands: {self.stand_count}", True, WHITE)
                #stands_text_rect = stands_text.get_rect(center=(WINDOW_WIDTH // 4, 220))
                #screen.blit(stands_text, stands_text_rect)

            if self.game_state != "waiting":
                self.draw_cards(self.dealer_cards, WINDOW_HEIGHT // 2 - 250)
                # Move player cards up
                self.draw_cards(self.player_cards, WINDOW_HEIGHT // 2 + 100)
                    
                # Draw hands value
                player_value = self.calculate_hand(self.player_cards)
                dealer_value = self.calculate_hand(self.dealer_cards)
                    
                value_font = pygame.font.Font(None, 30)
                player_text = value_font.render(f"Player Hand: {player_value}", True, WHITE)
                player_rect = player_text.get_rect(center=(WINDOW_WIDTH//2 + 250, WINDOW_HEIGHT - 125))
                screen.blit(player_text, player_rect)
                    
                if self.game_state == "game_over":
                    dealer_text = value_font.render(f"Dealer Hand: {dealer_value}", True, WHITE)
                    dealer_rect = dealer_text.get_rect(center=(WINDOW_WIDTH//2 + 250, WINDOW_HEIGHT//2 - 275))
                    screen.blit(dealer_text, dealer_rect)
                        
                    winner_text = font.render(self.current_winner, True, WHITE)
                    text_rect = winner_text.get_rect(center=(WINDOW_WIDTH//2 + 250, WINDOW_HEIGHT//2))
                    screen.blit(winner_text, text_rect)
                        
                    if not self.agent_playing:
                        self.hit_button.visible = False
                        self.stay_button.visible = False
                        self.start_button.visible = True
                        self.ai_button.visible = True

            if self.deck.reshuffle_warning:
                self.deck.init_deck()

            # Draw buttons
            self.start_button.draw(screen)
            self.hit_button.draw(screen)
            self.stay_button.draw(screen)
            self.ai_button.draw(screen)
            self.stop_button.draw(screen)
            self.speed_button.draw(screen)

            pygame.display.flip()
                
        pygame.quit()
        sys.exit()

def check_resources():
    """Check if all required resources are present"""
    if not os.path.exists(CARDS_DIR):
        print(f"Error: Cards directory not found at {CARDS_DIR}")
        return False
    
    required_files = ['back.png']
    suits = ['spades', 'clubs', 'hearts', 'diamonds']
    values = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
    
    for suit in suits:
        for value in values:
            required_files.append(f"{value}_of_{suit}.png")
    
    for file in required_files:
        if not os.path.exists(os.path.join(CARDS_DIR, file)):
            print(f"Error: Missing card image: {file}")
            return False
    
    return True

if __name__ == "__main__":
    if not check_resources():
        print("Error: Missing required resources. Please ensure all card images are present in the 'cards' directory.")
        sys.exit(1)
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)