# coding=utf-8
from uuid import uuid4

from client_logging import LogLevel


class PokerGame:
    ACTION = 'action'
    DEALT_CARD = 'dealt_card'
    FROM = 'ident'
    CARD_REVEAL = 'card_reveal'

    def __init__(self, max_players=3, blind=10):
        self.max_players = max_players
        self.blind = blind
        self.starting_cash = 200
        self.state_log = []
        self.dealer = 0
        self.last_raise = None

    def advance_to_next_dealer(self):
        if self.dealer == self.max_players:
            self.dealer = 0
        else:
            self.dealer += 1

    def new_raise(self) -> str:
        self.last_raise = str(uuid4())
        return self.last_raise


class PokerPlayer:
    POKER_PLAYER = 'poker_player'

    def __init__(self, ident, game: PokerGame):
        self.ident = ident
        self.game = game
        self.folded = False
        self.cash_in_hand = game.starting_cash
        self.cash_in_pot = 0
        self.did_play_blind_this_round = False
        self.last_raise_i_have_called = None
        self.hand = []
        self.winnings = 0

    def __str__(self):
        return "Player: {},\tCash in hand: {},\tCash in pot {}".format(self.ident,
                                                                       self.cash_in_hand,
                                                                       self.cash_in_pot)

    @property
    def is_all_in(self):
        return self.cash_in_hand == 0

    def add_to_pot(self, amount: int) -> bool:
        if self.cash_in_hand >= amount:
            self.cash_in_hand -= amount
            self.cash_in_pot += amount
            return True
        raise ValueError("Tried to add more to pot than possible!")

    def reset_blind_flag(self):
        self.did_play_blind_this_round = False

    def set_blind(self, logging_func, big_blind=True):
        self.did_play_blind_this_round = True
        if big_blind:

            self.game.state_log.append({
                PokerGame.FROM: self.ident,
                PokerGame.ACTION: BettingCodes.BIG_BLIND
            })
            logging_func(
                LogLevel.INFO,
                "Player {} plays BIG blind".format(
                    self.ident))

            if self.cash_in_hand < self.game.blind * 2:
                logging_func(LogLevel.INFO, "Going ALL IN for blind")
                self.add_to_pot(self.cash_in_hand)
            else:
                self.add_to_pot(self.game.blind * 2)
            self.game.new_raise()
        else:
            self.game.state_log.append({
                PokerGame.FROM: self.ident,
                PokerGame.ACTION: BettingCodes.SMALL_BLIND
            })
            logging_func(
                LogLevel.INFO,
                "Player {} plays SMALL blind".format(
                    self.ident))
            if self.cash_in_hand < self.game.blind:
                logging_func(LogLevel.INFO, "^^ goes ALL IN for blind")
                self.add_to_pot(self.cash_in_hand)
            else:
                self.add_to_pot(self.game.blind)


fresh_deck = list(range(10, 62))


class PokerWords:
    WINNINGS = 'winnings'
    OPEN_CARDS = 'open_cards'
    HAND = 'hand'
    DECK_STATE = 'deck_state'
    SHUFFLE_PLAYERS = 'shuffle_players'
    CRYPTODECK_STATE = 'crypto_deck_state'


class BettingCodes:
    CALL = 'call'
    BET = 'bet'
    FOLD = 'fold'
    ALLIN = 'all_in'
    SKIP = 'skip'
    BIG_BLIND = 'big_blind'
    SMALL_BLIND = 'small_blind'
