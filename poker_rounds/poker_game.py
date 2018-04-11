class PokerGame():
    ACTION = 'action'
    FROM = 'ident'
    CARD_REVEAL = 'card_reveal'
    def __init__(self, blind=10):
        self.blind = blind
        self.starting_cash = 100
        self.state_log = []
