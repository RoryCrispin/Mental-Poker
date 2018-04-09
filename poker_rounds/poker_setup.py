from poker_rounds.poker_game import PokerGame
from turn_taking_client import TurnTakingClient


class PokerSetup(TurnTakingClient):

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)

    def init_existing_state(self, state):
        self.build_player_map(state)
        super().init_existing_state(state)
        # if not self.have_built_poker_player_map(state):

    @staticmethod
    def have_built_poker_player_map(state):
        return PokerPlayer.POKER_PLAYER in list(state['peer_map'].items())[0][1]

    def build_player_map(self, state):
        print("-----------------------Poker Setup--------------")
        self.game = PokerGame()
        for _,  player in state['peer_map'].items():
            player[PokerPlayer.POKER_PLAYER] = PokerPlayer(self.game)

    def take_turn(self):
        print("turna")
        self.end_my_turn()

    def handle_turn(self, data):
        pass

    def is_round_over(self):
        state = {'peer_map': self.peer_map}
        return self.have_built_poker_player_map(state)




class PokerPlayer:
    POKER_PLAYER = 'poker_player'

    def __init__(self,  game: PokerGame):
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

