class PokerGame():
    ACTION = 'action'
    FROM = 'ident'
    CARD_REVEAL = 'card_reveal'
    def __init__(self, blind=10):
        self.blind = blind
        self.starting_cash = 1000000000
        self.state_log = []


class PokerPlayer:
    POKER_PLAYER = 'poker_player'

    def __init__(self, ident, game: PokerGame):
        self.ident = ident
        self.game = game
        self.action_log = []
        self.folded = False
        self.cash_in_hand = game.starting_cash
        self.cash_in_pot = 0

    def add_to_pot(self, amount: int) -> bool:
        if self.cash_in_hand >= amount:
            self.cash_in_hand -= amount
            self.cash_in_pot += amount
            return True
        return False

    def set_blind(self, big_blind=True):
        if big_blind:
            self.add_to_pot(self.game.blind * 2)
        else:
            self.add_to_pot(self.game.blind)

    def is_all_in(self):
        return self.cash_in_hand == 0


fresh_deck = list(range(10,62))


class PokerWords():
    OPEN_CARDS = 'open_cards'
    HAND = 'hand'
    DECK_STATE = 'deck_state'
    SHUFFLE_PLAYERS = 'shuffle_players'
    CRYPTODECK_STATE = 'crypto_deck_state'