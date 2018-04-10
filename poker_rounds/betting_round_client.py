from enum import Enum
from random import randint

from client_logging import LogLevel
from poker_rounds.poker_setup import PokerPlayer
from turn_taking_client import TurnTakingClient


class BettingCodes():
    CALL = 'call'
    BET = 'bet'
    FOLD = 'fold'
    ALLIN = 'all_in'


class BettingClient(TurnTakingClient):
    def __init__(self, cli, state=None, max_players=3, start_cash=100):
        self.player: PokerPlayer = None
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(BettingCodes.FOLD, self.handle_fold),
                               (BettingCodes.CALL, self.handle_call),
                               (BettingCodes.BET, self.handle_bet)
                               ])
        print("Run betting")
        self.have_init_state = False
        self.have_played_this_round = False

    def init_blinds(self):
        self.cli.log(LogLevel.VERBOSE, "Init Blinds")
        # TODO: we skip the first player because of next TODO
        bigb: PokerPlayer = self.get_peer_at_position(1)[1][PokerPlayer.POKER_PLAYER]
        bigb.set_blind(big_blind=True)

        lilb: PokerPlayer = self.get_peer_at_position(2)[1][PokerPlayer.POKER_PLAYER]
        lilb.set_blind(big_blind=False)

    def take_turn(self):
        print("tu--rn:")
        if not self.have_init_state:
            print("endy")
            self.end_my_turn()  # TODO: fix the problem that clients take turns before init_state has finished
        else:
            print("laalalal take turn")
            if not self.player.folded:
                i = randint(0, 10)
                print("do take turn")
                if i > 2:
                    self.make_call()
                else:
                    self.make_bet(randint(1, 5))
            self.end_my_turn()

    def make_call(self):
        self.logger.info("Making Call")
        self.have_played_this_round = True
        self.send_round_message(BettingCodes.CALL, {})

    def make_bet(self, amount: int):
        self.logger.info("Making bet of {}".format(amount))
        self.apply_bet(amount)

    def apply_bet(self, player: PokerPlayer, amount: int):
        return player.add_to_pot(amount)

    def init_existing_state(self, state):
        super().init_existing_state(state)
        self.init_blinds()
        self.player = self.peer_map[self.cli.ident][PokerPlayer.POKER_PLAYER]
        self.have_init_state = True

    def is_round_over(self):
        return False

    def get_active_pots(self):
        pass

    def handle_call(self, data):
        if self.is_turn_valid(data):
            pass

    def handle_fold(self, data):
        if self.is_turn_valid(data):
            pass

    def handle_bet(self, data):
        if self.is_turn_valid(data):
            pass
