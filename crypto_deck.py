class CryptoCard():
    ENCRYPTED = 'encrypted'
    DECRYPTED = 'decrypted'
    GENERATED = 'generated'
    ACTION = 'action'
    LOCKS_REMOVED = 'locks_removed'
    LOCKS_PRESENT = 'locks_present'
    VALUE = 'value'

    def __init__(self):
        self.state_log = []
        self.value = None
        self.locks_removed = []  # TODO: Make encryption use this class and swap this to LOCKS_ADDED
        self.locks_present = []
        self.dealt_to = None  # Identifies a the use of this card, ie: dealt to table /player 0

    def update_state(self, action, value):
        self.state_log.append({self.ACTION: action,
                               self.LOCKS_PRESENT: self.locks_present,
                               self.LOCKS_REMOVED: self.locks_removed,
                               self.VALUE: value})
        # self.locks_present = locks_present
        self.value = value

    def removed_lock(self, by, new_value):
        self.locks_removed.append(by)
        self.locks_present.remove(by)
        self.update_state(self.DECRYPTED, new_value)

    def generate_card(self, encrypted_by, value):
        self.locks_present = encrypted_by
        self.update_state(self.GENERATED, value)