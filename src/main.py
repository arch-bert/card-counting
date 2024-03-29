from blackjack.deck import Deck
from blackjack.hand import Hand
from entities.basic_strategy_player import BasicPlayer
from entities.dealer import Dealer
from copy import deepcopy
import random


def init_round(player, dealer, deck):
    """
    Initialize a round of blackjack.

    Parameters:
        player (BasicPlayer): The player object.
        dealer (Dealer): The dealer object.
        deck (Deck): The deck of cards.
    """

    # Create dummy-player variable (for splitting)
    dummy = None
    # Default bet (for non card-counting)
    bet = 1000

    # Determine count-adjusted bet
    if player.card_counting:
        adjusted_bet = player.calculate_bet(player.count, bet, deck.cards_left)
        player.start_round(deck, adjusted_bet)
    else:
        player.start_round(deck, bet)

    # Draw 2 cards and place bet
    dealer.start_round(deck, player)

    # Check for split
    decision = player.get_split_decision(dealer)
    if decision == 'y':

        dummy = player.split()

        # Do a manual hit_me()
        card = player.hand.cards.pop()
        dummy.hand.cards.append(card)
        player.hit_me(deck)
        dummy.hit_me(deck)

        if card.rank != 'ace':
            player.hand.value -= card.value
            dummy.hand.value += card.value

        # Play round with dummy-hand
        round(dummy, dealer, deck, dummy)

        # Add player and dummy's metrics together
        player.add_totals(dummy)

    # Normal round (no split)
    round(player, dealer, deck, dummy)


def round(player, dealer, deck, dummy):
    """
    Play a round of blackjack.

    Parameters:
        player (BasicPlayer): The player object.
        dealer (Dealer): The dealer object.
        deck (Deck): The deck of cards.
        dummy (BasicPlayer): The dummy player object for splitting (optional).
    """

    if dummy is not None and player.hand.cards[0].rank == 'ace':
        print(f'Bet: {player.current_bet}')
        player.hand.value = 11
        player.hand.aces = 1
        player.hit_me(deck)

    # Player decision loop (split NOT included)
    while not player.is_done:
        decision = player.get_other_decision(dealer)
        print(f'{player.name} decision: {decision}')
        if decision == 'h':
            player.hit_me(deck)
        elif decision == 's':
            player.stand()
        elif decision == 'd':
            player.hit_me(deck)
            player.doubles()
        print(f'{player.name} -> {player.hand}')

    # Dealer decision loop
    if player.hand.value < 21:
        while not dealer.is_done:
            decision = dealer.get_decision()
            print(f'Dealer decision: {decision}')
            if decision == 'h':
                dealer.hit_me(deck, player)
            elif decision == 's':
                dealer.stand()
            print(f'Dealer -> {dealer.hand}')

    # Check for busts
    if player.hand.value > 21:
        player.goes_bust()
    elif dealer.hand.value > 21:
        dealer.goes_bust()
        player.round_outcome(win=True)

    # Check for blackjack
    elif player.hand.value == 21 and len(player.hand.cards) == 2:
        player.gets_blackjack()

    # Compare raw hand values
    elif player.hand.value > dealer.hand.value:
        print('Comparing...')
        player.round_outcome(win=True)
        print('Comparing...')
    elif player.hand.value < dealer.hand.value:
        print('Comparing...')
        player.round_outcome(loss=True)
        print('Comparing...')
    else:
        player.round_outcome(draw=True)

    # Print end-of-round info
    print(f'{player.name}:', player.hand)
    print('Dealer:', dealer.hand)
    print(f'total earnings {player.total_earnings}')
    print('total bets:', player.total_bets)
    print('--------------------------------------')

    # Clear hands:
    dealer.hand = Hand()
    player.hand = Hand()

    # Reset dealer.is_done()
    dealer.is_done = False


if __name__ == '__main__':
    """
    Main function for playing multiple rounds of blackjack.

    Initialize game objects and play multiple rounds, then print a game summary.
    """

    # Initialize game objects for the entire game session
    deck = Deck(6)
    player = BasicPlayer("Player", card_counting=False)
    dealer = Dealer()

    # Number of rounds to play
    num_rounds = 1000  # Change this to play more or fewer rounds

    # Play multiple rounds
    for i in range(num_rounds):
        print(f"Round {i + 1}")
        init_round(player, dealer, deck)

    # Print game summary (total earnings, win rate, etc.) after all rounds are completed
    print("Game Summary")
    print(f'Total earnings {player.total_earnings}',
          f'Total bets {player.total_bets}',
          f'Ratio: {player.total_earnings/player.total_bets if player.total_bets != 0 else "N/A"}')
    print(
        f'Win rate: {player.wins/player.rounds if player.rounds != 0 else "N/A"}')
