class PokerGame():
    ACTION = 'action'
    FROM = 'ident'
    CARD_REVEAL = 'card_reveal'

    def __init__(self, blind=10, max_players=3):
        self.max_players = max_players
        self.blind = blind
        self.starting_cash = 200
        self.state_log = []
        self.dealer = 0

    def advance_to_next_dealer(self):
        if self.dealer == self.max_players:
            self.dealer = 0
        else:
            self.dealer += 1


class PokerPlayer:
    POKER_PLAYER = 'poker_player'

    def __init__(self, ident, game: PokerGame):
        self.ident = ident
        self.game = game
        self.action_log = []
        self.folded = False
        self.cash_in_hand = game.starting_cash
        self.cash_in_pot = 0
        self.did_play_blind_this_round = False

    def add_to_pot(self, amount: int) -> bool:
        if self.cash_in_hand >= amount:
            self.cash_in_hand -= amount
            self.cash_in_pot += amount
            return True
        raise ValueError("Tried to add more to pot than possible!")

    def reset_blind_flag(self):
        self.did_play_blind_this_round = False

    def set_blind(self, big_blind=True):
        from poker_rounds.betting_round_client import BettingCodes
        self.did_play_blind_this_round = True
        if big_blind:

            self.game.state_log.append({
                PokerGame.FROM: self.ident,
                PokerGame.ACTION: BettingCodes.BIG_BLIND
            })
            print("Player {} plays BIG blind".format(self.ident))

            if self.cash_in_hand < self.game.blind * 2:
                print("Going ALL IN for blind")
                self.add_to_pot(self.cash_in_hand)
            else:
                self.add_to_pot(self.game.blind * 2)
        else:
            self.game.state_log.append({
                PokerGame.FROM: self.ident,
                PokerGame.ACTION: BettingCodes.SMALL_BLIND
            })
            print("Player {} plays SMALL blind".format(self.ident))
            if self.cash_in_hand < self.game.blind:
                print("^^ goes ALL IN for blind")
                self.add_to_pot(self.cash_in_hand)
            else:
                self.add_to_pot(self.game.blind)

    def is_all_in(self):
        return self.cash_in_hand == 0


fresh_deck = list(range(10, 62))


class PokerWords():
    OPEN_CARDS = 'open_cards'
    HAND = 'hand'
    DECK_STATE = 'deck_state'
    SHUFFLE_PLAYERS = 'shuffle_players'
    CRYPTODECK_STATE = 'crypto_deck_state'
