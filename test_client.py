import logging
from multiprocessing import Pool

from time import sleep

from client import CommsClient, GreetingCli
from game_sequencer import ManualGameSequencer
from ordered_turn_client import InsecureOrderedClient
from poker_rounds.card_reveal_client import CardRevealClient
from poker_rounds.poker_game import PokerWords
from poker_rounds.poker_sequencer import PokerHandGameSequencer
from poker_rounds.secure_deck_shuffle import DeckShuffleClient
from secure_decryption_client import SecureShuffleSampleDecryptor
from secure_shuffle_client import SecureShufflingClient

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
    cli = CommsClient(round).begin()
    return cli


# def test_RSA_keys_match_three_way():
#     rounds = ManualGameSequencer([RSAKeyShareClient])
#     x = start_async_rounds(rounds, 3)
#     # For each client's state, extract it's own pubkey and ident as [(pk, id)]
#     actual_pubkeys = [(y['ident'], y['pubkey']) for y in x]
#     # Extract each player's list of external public keys
#     playerlists = [y['playerlist'] for y in x]
#
#     assert playerlists is not None
#     assert actual_pubkeys is not None
#
#     # Assert that all players lists of public keys match the actual values
#     for player in playerlists:
#         for pk_entry in player:
#             assert pk_entry in actual_pubkeys


def test_greeting_client():
    rounds = ManualGameSequencer([GreetingCli])
    x = start_async_rounds(rounds, 3)
    assert [y.get('greetings_sent') for y in x] == [2, 1, 0]


def test_insecure_ordering():
    """Assert that all clients produce the same ordering"""
    rounds = ManualGameSequencer([InsecureOrderedClient])
    x = start_async_rounds(rounds, 3)
    peermaps = [y['peer_map'] for y in x]
    assert all(x == peermaps[0] for x in peermaps)


from shuffling_client import ShufflingClient


def test_shuffling_client():
    rounds = ManualGameSequencer([ShufflingClient])
    x = start_async_rounds(rounds, 3)
    decks = [y['deck'] for y in x]
    assert (all(d == decks[0] for d in decks))
    assert (all(d != list(range(10)) for d in decks))


def test_secure_shuffling_client():
    rounds = ManualGameSequencer([SecureShufflingClient, SecureShuffleSampleDecryptor])
    x = start_async_rounds(rounds, 3)
    deck_states = []
    for client in x:
        deck_states.append(client.get(PokerWords.DECK_STATE))
    assert deck_states[0] != list(range(1, 10))
    # There's a 10! chance that this test will fail because the shuffled order
    # is actually 1..10
    assert sorted(deck_states[0]) == list(range(1, 10))
    assert (all(d == deck_states[0] for d in deck_states))


def test_secure_deck_shuffling():
    rounds = ManualGameSequencer([DeckShuffleClient, SecureShuffleSampleDecryptor])
    x = start_async_rounds(rounds, 3)
    deck_states = []
    for client in x:
        deck_states.append(client.get(PokerWords.DECK_STATE))
    assert deck_states[0] != list(range(10, 62))
    assert sorted(deck_states[0]) == list(range(10, 62))
    assert (all(d == deck_states[0] for d in deck_states))


def test_card_reveal_client():
    rounds = ManualGameSequencer([DeckShuffleClient, CardRevealClient])
    x = start_async_rounds(rounds, 3)
    for state in x:
        if state['crypto_deck_state'][0].locks_present is []:
            assert state['crypto_deck_state'][0].value in range(10, 62)


def test_hand_reveal_client():
    poker_sequencer = PokerHandGameSequencer()
    x = start_async_rounds(poker_sequencer, 3)
    for state in x:
        assert len(state.get(PokerWords.HAND)) == 2

    # Check betting round works
    peer_maps = [y['peer_map'] for y in x]
    playermaps = []
    for client_pm in peer_maps:
        for _, playermap in client_pm.items():
            playermaps.append(playermap['poker_player'])
    assert all((d.cash_in_pot == playermaps[0].cash_in_pot for d in playermaps))


def test_lots_of_rounds():
    for _ in range(0, 20):
        poker_sequencer = PokerHandGameSequencer()
        x = start_async_rounds(poker_sequencer, 3)
