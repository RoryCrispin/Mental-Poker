# coding=utf-8
from crypto_deck import CryptoCard
from poker_rounds.poker_game import PokerWords
from secure_shuffle_client import SecureShufflingClient


class DeckShuffleClient(SecureShufflingClient):
    def __init__(self, cli, state=None):
        super().__init__(cli, state)
        self.shuffle_state = list(range(10, 62))

    def get_final_state(self):
        state = super().get_final_state()
        state.update({
            PokerWords.DECK_STATE: self.shuffle_state,
            PokerWords.CRYPTODECK_STATE: self.init_cryptodeck()
        })
        return state

    def init_cryptodeck(self):
        cryptodeck = []
        i = 0
        for card in self.shuffle_state:
            cryptocard = CryptoCard()
            cryptocard.generate_card(self.encryptd_by, card, i)
            cryptodeck.append(cryptocard)

        # Prepare the card with their assigned player.
        index = 0
        for player_index in range(0, self.max_players):
            for _ in range(0, 2):
                cryptodeck[index].dealt_to = player_index
                index += 1
        # Prepare the table cards
        for index in range(0, 5):
            location = (self.max_players * 2) + index
            cryptodeck[location].dealt_to = -1 - index
        return cryptodeck
