import os.path
import time

from yaml import dump

from client import CommsClient
from poker_rounds.betting_player import HumanBettingPlayer
from poker_rounds.poker_sequencer import PokerHandGameSequencer

ai_betting_player = HumanBettingPlayer()
rounds = PokerHandGameSequencer()
cli = CommsClient(rounds, {'betting_player': ai_betting_player}).begin()

print("~~~~~~~ Game State Log ~~~~~~~~~~")
print(dump(cli['game'].state_log))
scriptpath = os.path.dirname(__file__)
filename = os.path.join(scriptpath, 'states/{}_{}.txt'.format(time.time(), cli['peer_map'][cli['ident']]['roll']))

with open(filename, 'w') as f:
    f.write(dump(cli))
    f.close()
pass
