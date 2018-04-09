from enum import Enum

from client_logging import LogLevel
from poker_rounds.poker_setup import PokerPlayer
from turn_taking_client import TurnTakingClient


class BettingCodes(Enum):
    CALL = 0
    BET = 1
    FOLD = 2
    ALLIN = 3


class BettingClient(TurnTakingClient):
    def __init__(self, cli, state=None, max_players=3, start_cash=100):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([])
        print("Run betting")

    def init_blinds(self):
        self.cli.log(LogLevel.VERBOSE, "Init Blinds")
        _, bigb = self.get_peer_at_position(0)
        bigb[PokerPlayer.POKER_PLAYER].set_blind(big_blind=True)
        _, lilb = self.get_peer_at_position(1)
        lilb[PokerPlayer.POKER_PLAYER].set_blind(big_blind=False)

    def take_turn(self):
        print("b turn")
        self.end_my_turn()

    def init_existing_state(self, state):
        super().init_existing_state(state)
        self.init_blinds()

    def is_round_over(self):
        return False
