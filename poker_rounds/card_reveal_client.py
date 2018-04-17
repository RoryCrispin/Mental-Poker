# coding=utf-8
from client_logging import LogLevel
from crypto_deck import CryptoCard, CryptoWords
from poker_rounds.poker_game import PokerWords
from turn_taking_client import TurnTakingClient


class CardRevealClient(TurnTakingClient):
    NOT_SHARING_PRIVATE = 'not_sharing_private'
    REMOVE_LOCK = 'remove_lock'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.NOT_SHARING_PRIVATE,
                                self.recv_not_sharing_private),
                               (self.REMOVE_LOCK,
                                self.recv_lock_removed)])
        self.card = CryptoCard()
        self.cryptodeck_state = None
        self.key = None
        self.hand = None

    def init_existing_state(self, state):
        self.cryptodeck_state = state[PokerWords.CRYPTODECK_STATE]
        self.card = self.get_card_for_decryption()
        self.key = state[CryptoWords.SRA_KEY]
        super().init_existing_state(state)

    def get_card_for_decryption(self):
        index = 0
        for card in self.cryptodeck_state:
            if self.card.dealt_to is None:
                pass
            try:
                if card.dealt_to >= 0 and not card.has_been_dealt:
                    return card
            except TypeError:
                return None
            index += 1
        return None

    def take_turn(self):
        if self.is_my_card():
            self.send_round_message(self.NOT_SHARING_PRIVATE, {})
            self.cli.log(LogLevel.VERBOSE, "Not sharing my private key")
            self.end_my_turn()
        else:
            self.cli.log(LogLevel.VERBOSE, "Removed my lock")
            self.remove_my_lock_and_share()
            self.end_my_turn()

    def remove_my_lock_and_share(self):  # TODO: join this with remove_my_lock method
        if self.card.value is None:
            self.card = self.get_card_for_decryption()
        self.remove_my_lock()
        self.send_round_message(self.REMOVE_LOCK, {self.REMOVE_LOCK: self.card.value})

    def remove_my_lock(self):
        decrypted_card = self.key.decrypt_message(self.card.value)
        self.card.removed_lock(self.cli.ident, decrypted_card)

    def recv_lock_removed(self, data):
        if self.is_turn_valid(data):
            self.card.removed_lock(data[self.SENDER_ID], data['data'][self.REMOVE_LOCK])
            self.cli.log(LogLevel.VERBOSE, "Recv lock removed by {}".format(data[self.SENDER_ID]))

            if self.received_all_peer_keys() and self.is_my_card():
                self.remove_my_lock()
                self.cli.log(LogLevel.INFO, "Received locked card: {}".format(self.card.value))

    def is_card_valid(self):
        if self.card.value in range(10, 62):
            return True
        else:
            self.cli.log(LogLevel.ERROR, "Generated an invalid cardlib!")
            raise ValueError

    def recv_not_sharing_private(self, data):
        if self.is_turn_valid(data):
            pass

    def is_my_card(self):
        return self.generating_card_for() == self.cli.ident

    def generating_card_for(self):
        # return self.get_ident_at_position(0)
        return self.get_ident_at_position(self.card.dealt_to)

    def received_all_peer_keys(self):
        if len(self.card.locks_present) == 0:
            self.card.has_been_dealt = True
            return True
        if len(self.card.locks_present) == 1 and \
                self.card.locks_present[0] == self.generating_card_for():
            self.card.has_been_dealt = True
            return True
        return False

    def is_round_over(self):
        if self.card is None:
            return True
        return self.received_all_peer_keys()

    def get_final_state(self):
        state = super().get_final_state()
        state.update({PokerWords.CRYPTODECK_STATE: self.cryptodeck_state})
        return state


class HandDecoder(TurnTakingClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.hand = None

    def init_existing_state(self, state):
        super().init_existing_state(state)
        hand = []
        for card in state['crypto_deck_state']:
            if self.get_my_position() == card.dealt_to:
                hand.append(card.value)
        self.hand = hand

    def get_final_state(self):
        state = super().get_final_state()
        state.update({PokerWords.HAND: self.hand})
        return state

    def is_round_over(self):
        return self.hand is not None

    def take_turn(self):
        self.end_my_turn()
