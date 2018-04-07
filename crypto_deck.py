class CryptoCard():
    ENCRYPTED = 'encrypted'
    DECRYPTED = 'decrypted'
    GENERATED = 'generated'
    ACTION = 'action'
    LOCKS_REMOVED = 'locks_removed'
    VALUE = 'value'

    def __init__(self):
        self.state_log = []
        self.value = None
        self.locks_removed = []  # TODO: Make encryption use this class and swap this to LOCKS_ADDED
        self.locks_present = []
        self.dealt_to = None  # Identifies a the use of this card, ie: dealt to table /player 0

    def update_state(self, action, author, value):
        self.state_log.append({self.ACTION: action,
                               self.LOCKS_REMOVED: author,
                               self.VALUE: value})
        self.value = value

    def removed_lock(self, by, new_value):
        self.locks_removed.append(by)
        self.update_state(self.DECRYPTED, self.locks_removed[:], new_value)
