from turn_taking_client import TurnTakingClient
from crypto_deck import CryptoWords
from poker_rounds.poker_helper import PokerWords


class SecureDecryptionClient(TurnTakingClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(CryptoWords.SHARE_PRIVATE, self.recv_private_component)])
        self.deck_state = None
        self.key = None
        self.have_shared_my_component = False

    def init_existing_state(self, state):
        self.deck_state = state[PokerWords.DECK_STATE]
        self.key = state[CryptoWords.SRA_KEY]
        super().init_existing_state(state)

    def init_no_state(self):
        raise ValueError

    def take_turn(self):
        self.share_my_private_component()

    def share_my_private_component(self):
        print("shared my componrnt")
        self.have_shared_my_component = True
        self.send_round_message(CryptoWords.SHARE_PRIVATE, {
            CryptoWords.SHARE_PRIVATE: self.key.get_private_component()
        })
        self.end_my_turn()

    def recv_private_component(self, data):
        if self.is_turn_valid(data):
            print("recv component")
            self.peer_map[data[self.SENDER_ID]][CryptoWords.PRIVATE_COMPONENT] =\
                data['data'][CryptoWords.SHARE_PRIVATE]

    def decrypt_deck(self, key=None):
        if key is None:
            key = self.key
        new_deck = []
        for card in self.deck_state:
            new_deck.append(self.key.decrypt_message(card))
        self.deck_state = new_deck

    def is_round_over(self):
        for ident, vals in self.peer_map.items():
            if ident != self.cli.ident:
                if vals.get(CryptoWords.PRIVATE_COMPONENT) is None:
                    return False
        return self.have_shared_my_component

    def fully_decrypt_deck(self):
        self.decrypt_deck()
        print("Decrypt with {}".format(self.cli.ident))
        own_priv = self.key.get_private_component()
        for ident, vals in self.peer_map.items():
            if ident != self.cli.ident:
                d = vals.get(CryptoWords.PRIVATE_COMPONENT)
                print("Decrpt with {}".format(ident))
                self.key.update_private_component(d)
                self.decrypt_deck()
        self.key.update_private_component(own_priv)


class SecureShuffleSampleDecryptor(SecureDecryptionClient):
    def get_final_state(self):
        self.fully_decrypt_deck()
        state = super().get_final_state()
        state.update({PokerWords.DECK_STATE: self.deck_state})
        return state
