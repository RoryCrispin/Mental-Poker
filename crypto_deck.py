# coding=utf-8
from cardlib.Card import Card


class CryptoCard:
    ENCRYPTED = 'encrypted'
    DECRYPTED = 'decrypted'
    GENERATED = 'generated'
    ACTION = 'action'
    LOCKS_REMOVED = 'locks_removed'
    LOCKS_PRESENT = 'locks_present'
    VALUE = 'value'
    SHOWDOWN_DECRYPT = 'showdown_decrypt'

    def __init__(self):
        self.state_log = []
        self.value = None
        self.locks_present = []
        self.dealt_to = None  # Identifies a the use of this card, ie: dealt to table /player 0
        self.has_been_dealt = False
        self.deck_index = None

    def update_state(self, action, value):
        self.state_log.append({self.ACTION: action,
                               self.LOCKS_PRESENT: self.locks_present.copy(),
                               self.VALUE: value})
        self.value = value

    def removed_lock(self, by, new_value):
        self.locks_present.remove(by)
        self.update_state(self.DECRYPTED, new_value)

    def generate_card(self, encrypted_by, value, deck_index):
        self.deck_index = deck_index
        self.locks_present = encrypted_by.copy()
        self.update_state(self.GENERATED, value)

    def showdown_decrypt(self, value):
        self.locks_present.clear()
        self.update_state(self.SHOWDOWN_DECRYPT, value)

    def get_card(self):
        if not self.locks_present:
            return Card(self.value)
        else:
            print("Not fully decrypted!")
            return None


class CryptoWords:
    SHARE_PRIVATE = 'share_private'
    SRA_KEY = 'sra_key'
    PRIVATE_COMPONENT = 'private_component'
