import logging
from multiprocessing import Pool
from time import sleep

from client import Client, GreetingCli
from ordered_turn_client import InsecureOrderedClient
from rsa_client import RSAKeyShareClient
from secure_deck_shuffle import DeckShuffleClient
from secure_decryption_client import SecureShuffleSampleDecryptor
from secure_shuffle_client import SecureShufflingClient
from words import PokerWords

logger = logging.getLogger()


def start_async_rounds(round, process_count):
    # Each process needs to start with a slight delay to prevent race conditions
    sleepmap = [0.1 * x for x in range(0, process_count)]
    start_delay = max(sleepmap) + 0.1
    args = [(round, s, start_delay) for s in sleepmap]
    p = Pool(processes=process_count)
    pmap = p.map_async(start_game, args)
    return pmap.get()


def start_game(args):
    round, sleeptime, start_delay = args
    sleep(sleeptime)
    cli = Client(round).begin()
    return cli


def test_RSA_keys_match_three_way():
    x = start_async_rounds([RSAKeyShareClient], 3)
    # For each client's state, extract it's own pubkey and ident as [(pk, id)]
    actual_pubkeys = [(y['ident'], y['pubkey']) for y in x]
    # Extract each player's list of external public keys
    playerlists = [y['playerlist'] for y in x]

    assert playerlists is not None
    assert actual_pubkeys is not None

    # Assert that all players lists of public keys match the actual values
    for player in playerlists:
        for pk_entry in player:
            assert pk_entry in actual_pubkeys


def test_greeting_client():
    x = start_async_rounds([GreetingCli], 3)
    assert [y.get('greetings_sent') for y in x] == [2, 1, 0]


def test_insecure_ordering():
    """Assert that all clients produce the same ordering"""
    x = start_async_rounds([InsecureOrderedClient], 3)
    peermaps = [y['peer_map'] for y in x]
    assert all(x == peermaps[0] for x in peermaps)


from shuffling_client import ShufflingClient


def test_shuffling_client():
    x = start_async_rounds([ShufflingClient], 3)
    decks = [y['deck'] for y in x]
    assert (all(d == decks[0] for d in decks))
    assert (all(d != list(range(10)) for d in decks))


def test_secure_shuffling_client():
    x = start_async_rounds([SecureShufflingClient, SecureShuffleSampleDecryptor], 3)
    deck_states = []
    for client in x:
        deck_states.append(client.get(PokerWords.DECK_STATE))
    assert deck_states[0] != list(range(1, 10))  # This may fail if the shuffled list actually results in 1..9...
    assert sorted(deck_states[0]) == list(range(1, 10))
    assert (all(d == deck_states[0] for d in deck_states))


def test_secure_deck_shuffling():
    x = start_async_rounds([DeckShuffleClient, SecureShuffleSampleDecryptor], 3)
    deck_states = []
    for client in x:
        deck_states.append(client.get(PokerWords.DECK_STATE))
    assert deck_states[0] != list(range(10, 62))  # This may fail if the shuffled list actually results in 1..9...
    assert sorted(deck_states[0]) == list(range(10, 62))
    assert (all(d == deck_states[0] for d in deck_states))
