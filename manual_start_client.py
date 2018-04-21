# coding=utf-8
import time

from client import CommsClient
from poker_rounds.betting_player import AIBettingPlayer
from poker_rounds.poker_sequencer import PokerHandGameSequencer

ai_betting_player = AIBettingPlayer()
rounds = PokerHandGameSequencer()

cli, am = CommsClient(rounds, {'betting_player': ai_betting_player}).begin()

print("- [Game Over, {}]".format(time.time()))

print(am)
