from client import GameClient
from poker_rounds.poker_game import PokerGame
from turn_taking_client import TurnTakingClient


class PokerSetup(GameClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state)

    def init_existing_state(self, state):
        super().init_existing_state(state)
        self.build_player_map(state)

    @staticmethod
    def have_built_poker_player_map(state):
        return PokerPlayer.POKER_PLAYER in list(state['peer_map'].items())[0][1]

    def build_player_map(self, state):
        print("-----------------------Poker Setup--------------")
        self.game = PokerGame()
        for ident, player in state['peer_map'].items():
            player[PokerPlayer.POKER_PLAYER] = PokerPlayer(ident, self.game)
        self.peer_map = state['peer_map']

    def is_round_over(self):
        state = {'peer_map': self.peer_map}
        return self.have_built_poker_player_map(state)

    def get_final_state(self):
        state = super().get_final_state()
        state.update({'peer_map': self.peer_map})
        return state


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
