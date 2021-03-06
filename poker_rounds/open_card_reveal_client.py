# coding=utf-8
from client_logging import LogLevel
from poker_rounds.card_reveal_client import CardRevealClient
from poker_rounds.poker_game import PokerGame


class OpenCardRevealClient(CardRevealClient):
    """Extends the CardRevealClient to reveal open cards on the table
    (Ie, flop turn, and river cards)"""
    def take_turn(self):
        self.cli.log(LogLevel.INFO, "Removed my lock of communal card")
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
            except TypeError:
                return None
            index += 1
        raise ValueError("No card to decrypt")

    def generating_card_for(self):
        return self.card.dealt_to

    def received_all_peer_keys(self):
        return len(self.card.locks_present) == 0

    def get_final_state(self):
        self.cli.log(
            LogLevel.INFO,
            "Got community card: {}".format(
                self.card.value))
        self.card.has_been_dealt = True
        state = super().get_final_state()
        state['game'].state_log.append(
            {PokerGame.CARD_REVEAL: str(self.card.get_card())})
        return state
