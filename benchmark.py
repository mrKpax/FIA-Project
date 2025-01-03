import random
from benchmark_bj import Card, Deck
import csv
import os

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

def decide_action(dealer_hand, player_hand):
    pvalue = hand_value(player_hand)
    d_upcard = hand_value(dealer_hand[:1])

    if any(card.number == 'A' for card in player_hand):
        if pvalue >= 19:
            action = "stay"
        elif pvalue == 18:
            if d_upcard <= 8:
                action = "stay"
            else:
                action = "hit"
        else:
            action = "hit"
    elif pvalue >= 17:
        action = "stay"
    elif pvalue >= 13 and pvalue <= 16:
        if d_upcard >= 7:
            action = "hit"
        else:
            action = "stay"
    elif pvalue == 12:
        if d_upcard >= 4 and d_upcard <= 6:
            action = "stay"
        else:
            action = "hit"
    else:  # Player value <= 11
        action = "hit"
        
    return action

def log_data(log_file, dealer_upvalue, first_pvalue, ace, first_action, result):
    with open(log_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([dealer_upvalue, first_pvalue, ace, first_action, result])

def main(num_rounds):
    running = True
    wins = losses = draws = games = 0
    log_file = "game_log.csv"
    deck = Deck()

    if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
            with open(log_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Dealer Card", "Player Value", "Ace", "Action", "Reward"
                ])        

    for round_number in range(1, num_rounds + 1):
        print(f"\n==================== NEW ROUND ====================")

        dealer_hand = [deck.deal_card(), deck.deal_card()]
        player_hand = [deck.deal_card(), deck.deal_card()]
        game_over = False
        dealer_turn = False

        # value for csv log
        first_pvalue = hand_value(player_hand)
        dealer_upvalue = hand_value(dealer_hand[:1])
        ace = any(card.number == 'A' for card in player_hand)
        first_action = None
        result = None

        while not game_over:
            print("\nDealer's cards:", Card.format_cards(dealer_hand[:1]), "[?]")
            print("Player's cards:", Card.format_cards(player_hand), "=>", hand_value(player_hand))

            action = decide_action(dealer_hand, player_hand)
            if first_action is None:
                first_action = action

            ace = any(card.number == 'A' for card in player_hand)

            if action == "hit":
                player_hand.append(deck.deal_card())
            elif action == "stay":
                dealer_turn = True
            else:
                print("Invalid action. Please type [hit/stay].")

            game_over, winner = game_result(dealer_turn, player_hand, dealer_hand)

            if dealer_turn:
                while hand_value(dealer_hand) < 17: # dealer stay on 17
                    dealer_hand.append(deck.deal_card())
                game_over, winner = game_result(dealer_turn, player_hand, dealer_hand)

        print("\nDealer's cards:", Card.format_cards(dealer_hand), "=>", hand_value(dealer_hand))
        print("Player's cards:", Card.format_cards(player_hand), "=>", hand_value(player_hand))
        print("\n==================== GAME OVER ====================")

        if winner is None:
            print("\nTie!")
            draws += 1
            result = 0
        elif winner:
            if is_blackjack(player_hand):
                print("\nPlayer wins with a Blackjack!")
            else:
                print("\nPlayer wins!")
            wins += 1
            result = 1
        else:
            print("\nDealer wins!")
            losses += 1
            result = -1

        log_data(log_file, dealer_upvalue, first_pvalue, ace, first_action, result)

        games += 1

        deck.shuffle_if_needed()

    print(f"\nGames: {games}, Wins: {wins}, Losses: {losses}, Draws: {draws}")
    win_per = (wins * 100)/games
    print(f"Wins percentage: {win_per:.2f}")

if __name__ == "__main__":
    main(num_rounds=1000)