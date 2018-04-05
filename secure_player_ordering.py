from secure_shuffle_client import SecureShufflingClient
from secure_decryption_client import SecureDecryptionClient
from words import PokerWords

class PlayerShuffleClient(SecureShufflingClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)


    def alert_players_have_been_ordered(self):
        print("Setting deck!")
        self.shuffle_state = self.get_player_idents()
        super().alert_players_have_been_ordered()

    def get_player_idents(self):
        idents = []
        for ident, _ in self.peer_map.items():
            pass
