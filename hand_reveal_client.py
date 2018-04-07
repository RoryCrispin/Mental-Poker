from crypto_deck import CryptoCard
from pkr_logging import LogLevel
from turn_taking_client import TurnTakingClient
from words import PokerWords, CryptoWords


class HandRevealClient(TurnTakingClient):
    NOT_SHARING_PRIVATE = 'not_sharing_private'
    REMOVE_LOCK = 'remove_lock'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.NOT_SHARING_PRIVATE,
                                self.recv_not_sharing_private),
                               (self.REMOVE_LOCK,
                                self.recv_lock_removed)])
        self.card = CryptoCard()

    def init_existing_state(self, state):
        self.deck_state = state[PokerWords.DECK_STATE]
        self.key = state[CryptoWords.SRA_KEY]
        super().init_existing_state(state)

    def take_turn(self):
        if self.is_my_card():
            self.send_round_message(self.NOT_SHARING_PRIVATE, {})
            self.cli.log(LogLevel.VERBOSE, "Not sharing")
            self.end_my_turn()
        else:
            self.cli.log(LogLevel.VERBOSE, "Removed my lock")
            self.remove_my_lock_and_share()
            self.end_my_turn()

    def remove_my_lock_and_share(self):  # TODO: join this with remove_my_lock method
        if self.card.value is None:
            self.card.update_state(CryptoCard.GENERATED, self.cli.ident,
                                   self.deck_state[0])  # TODO: Extend the deck
        decrypted_card = self.key.decrypt_message(self.card.value)
        self.card.removed_lock(self.cli.ident, decrypted_card)
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
            self.cli.log(LogLevel.ERROR, "Generated an invalid card!")
            raise ValueError

    def recv_not_sharing_private(self, data):
        if self.is_turn_valid(data):
            pass

    def is_my_card(self):
        return self.generating_card_for() == self.cli.ident

    def generating_card_for(self):
        return self.get_ident_at_position(0)

    def received_all_peer_keys(self):
        return len(self.card.locks_removed) >= (self.max_players - 1)

    def is_round_over(self):
        return self.received_all_peer_keys()