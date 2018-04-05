from random import shuffle

from turn_taking_client import TurnTakingClient
from client import LogLevel
from crypto.makeRsaKeys import SRA_key
from words import PokerWords, CryptoWords


class SecureShufflingClient(TurnTakingClient, CryptoWords):
    SHUFFLE_DECK = 'shuffle_deck'
    SHARE_PRIMES = 'share_primes'
    SHARE_KEY = 'share_key'
    SHARE_PRIVATE = 'share_private'
    ENCRYPTED_BY = 'encrypted_by'
    KEYSIZE = 256
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.SHUFFLE_DECK, self.recv_shuffled_deck),
                               (self.SHARE_PRIMES, self.recv_primes)
                               ])

        self.shuffle_state = list(range(1,10))
        self.shuffled_times = 0
        self.private_components = []
        self.encryptd_by = []


    def take_turn(self):
        self.shuffled_times += 1
        if self.is_first_turn():
            self.share_primes()

        self.cli.log(LogLevel.INFO, "Shuffled deck")
        self.encryptd_by.append(self.cli.ident)
        self.encrypt_deck()
        print("Actually shuffling!")
        shuffle(self.shuffle_state)

        self.send_round_message(self.SHUFFLE_DECK, {
            self.SHUFFLE_DECK: self.shuffle_state,
            self.ENCRYPTED_BY: self.encryptd_by})
        self.end_my_turn()

    def share_primes(self):
        self.key = SRA_key.from_new_primes(self.KEYSIZE)
        self.send_round_message(self.SHARE_PRIMES,
                                {self.SHARE_PRIMES:
                                 self.key.get_public_primes()})

    def encrypt_deck(self):
        new_deck = []
        for card in self.shuffle_state:
            new_deck.append(self.key.encrypt_message(card))
        self.shuffle_state = new_deck


    def recv_shuffled_deck(self, data):
        if self.is_turn_valid(data):
            self.cli.log(LogLevel.INFO, "Got shuffled deck")
            self.shuffle_state = data['data'][self.SHUFFLE_DECK]
            self.encryptd_by = data['data'][self.ENCRYPTED_BY]
            self.shuffled_times += 1

    def recv_primes(self, data):
        if self.is_turn_valid(data):
            self.pq = data['data'][self.SHARE_PRIMES]
            self.key = SRA_key.from_existing_primes(self.KEYSIZE, self.pq)

    def is_round_over(self):
        return len(self.encryptd_by) >= self.max_players

    def get_final_state(self):
        state = super().get_final_state()
        state.update({
            PokerWords.DECK_STATE: self.shuffle_state,
            CryptoWords.SRA_KEY: self.key
        })
        return state
