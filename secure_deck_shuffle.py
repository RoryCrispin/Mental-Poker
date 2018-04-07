from secure_shuffle_client import SecureShufflingClient
from secure_decryption_client import SecureDecryptionClient
from words import PokerWords, CryptoWords
from turn_taking_client import TurnTakingClient
from poker_helper import fresh_deck


class DeckShuffleClient(SecureShufflingClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.shuffle_state = list(range(10, 62))
