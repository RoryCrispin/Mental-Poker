# coding=utf-8
from secure_shuffle_client import SecureShufflingClient


class DeckShuffleClient(SecureShufflingClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.shuffle_state = list(range(10, 62))
