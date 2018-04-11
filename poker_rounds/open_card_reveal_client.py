from poker_rounds.card_reveal_client import CardRevealClient
from poker_rounds.poker_helper import PokerWords
from src.game.Log import LogLevel


class OpenCardRevealClient(CardRevealClient):
    def take_turn(self):
        self.cli.log(LogLevel.INFO, "Removed my lock of communal cardlib")
        self.remove_my_lock_and_share()
        self.end_my_turn()

    def get_card_for_decryption(self):
        index = 0
        for card in self.cryptodeck_state:
            if self.card.dealt_to is None:
                pass
            try:
                if card.dealt_to <= 0 and not card.has_been_dealt:
                    return card
            except(TypeError):
                return None
            index += 1
        return None

    def generating_card_for(self):
        return self.card.dealt_to

    def received_all_peer_keys(self):
        return len(self.card.locks_present) == 0

    def get_final_state(self):
        self.cli.log(LogLevel.INFO, "Got community cardlib: {}".format(self.card.value))
        self.card.has_been_dealt = True
        state = super().get_final_state()
        if state.get(PokerWords.OPEN_CARDS) is None:
            state[PokerWords.OPEN_CARDS] = []
        # state[PokerWords.OPEN_CARDS].append(self.cardlib)
        state[PokerWords.OPEN_CARDS].append((self.card.dealt_to, self.card.value))
        return state

