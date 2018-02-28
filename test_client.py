from multiprocessing import Pool
from time import sleep
from Client import Client
from RSAClient import RSAKeyShareClient
import logging

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
    x = start_async_rounds(RSAKeyShareClient, 3)
    # For each client's state, extract it's own pubkey and ident as [(pk, id)]
    actual_pubkeys = [(y[1]['ident'], y[1]['pubkey']) for y in x]
    # Extract each player's list of external public keys
    playerlists = [y[1]['playerlist'] for y in x]

    assert playerlists is not None
    assert actual_pubkeys is not None

    # Assert that all players lists of public keys match the actual values
    for player in playerlists:
        for pk_entry in player:
            assert pk_entry in actual_pubkeys
