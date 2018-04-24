# coding=utf-8
import time
from yaml import dump

from client import CommsClient
from poker_rounds.betting_player import AIBettingPlayer
from poker_rounds.poker_sequencer import PokerGameSequencer

"""This is a testing client which simply starts the game. It's used by debugging scripts only.
Users should see run.py instead."""

ai_betting_player = AIBettingPlayer()
rounds = PokerGameSequencer()

cli = CommsClient(rounds, {'betting_player': ai_betting_player, 'log_level': 0}).begin()

print("- [Game Over, {}]".format(time.time()))

print("~~~~~~~ Game State Log ~~~~~~~~~~")
print(dump(cli['game'].state_log))
print("My Ident: %s" % cli['ident'])

