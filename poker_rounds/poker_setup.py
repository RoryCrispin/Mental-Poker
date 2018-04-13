from client import GameClient
from poker_rounds.poker_game import PokerGame, PokerPlayer


class PokerSetup(GameClient):
    def __init__(self, cli, state=None, max_players=3):
        self.max_players = max_players
        super().__init__(cli, state)

    def init_existing_state(self, state):
        super().init_existing_state(state)
        self.build_player_map(state)

    @staticmethod
    def have_built_poker_player_map(state):
        return PokerPlayer.POKER_PLAYER in list(state['peer_map'].items())[0][1]

    def build_player_map(self, state):
        self.game = PokerGame(self.max_players)
        for ident, player in state['peer_map'].items():
            player[PokerPlayer.POKER_PLAYER] = PokerPlayer(ident, self.game)
        self.peer_map = state['peer_map']

    def is_round_over(self):
        state = {'peer_map': self.peer_map}
        return self.have_built_poker_player_map(state)

    def get_final_state(self):
        state = super().get_final_state()
        state.update({'peer_map': self.peer_map,
                      'game': self.game})
        return state


