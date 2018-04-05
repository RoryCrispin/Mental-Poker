from client import LogLevel
from crypto.makeRsaKeys import SRA_key
from turn_taking_client import TurnTakingClient
from secure_shuffle_client import PokerWords, CryptoWords


class SecureDecryptionClient(TurnTakingClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(CryptoWords.SHARE_PRIVATE, self.recv_private_component)])
        self.deck_state = None
        self.key = None
        self.private_components = []
        self.have_shared_my_component = False

    def init_existing_state(self, state):
        self.deck_state = state[PokerWords.DECK_STATE]
        self.key = state[CryptoWords.SRA_KEY]
        super().init_existing_state(state)

    def init_no_state(self):
        raise ValueError

    def take_turn(self):
        # TODO: If it's my card reveal, dont share my component
        self.share_my_private_component()

    def share_my_private_component(self):
        print("shared my componrnt")
        self.have_shared_my_component = True
        self.send_round_message(CryptoWords.SHARE_PRIVATE, {
            CryptoWords.SHARE_PRIVATE: self.key.get_private_component()
        })
        self.end_my_turn()

    def recv_private_component(self, data):
        print("recv component")
        if self.is_turn_valid(data):
            self.private_components.append(
                (data[self.SENDER_ID], data['data'][CryptoWords.SHARE_PRIVATE]))

    def decrypt_deck(self, key=None):
        if key is None:
            key = self.key
        new_deck = []
        for card in self.deck_state:
            new_deck.append(self.key.decrypt_message(card))
        self.deck_state = new_deck

    def is_game_over(self):
        return len(self.private_components) == 2 and self.have_shared_my_component

    def get_final_state(self):
        assert self.deck_state != [52]
        state = super().get_final_state()
        print("Decrypt with {}".format(self.cli.ident))
        self.decrypt_deck()
        for id, d in self.private_components:
            print("Decrpt with {}".format(id))
            self.key.update_private_component(d)
            self.decrypt_deck()
        assert self.deck_state == list(range(1,10))