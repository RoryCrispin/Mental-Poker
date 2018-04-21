# coding=utf-8
import time

from client import CommsClient
from poker_rounds.betting_player import AIBettingPlayer
from poker_rounds.poker_sequencer import PokerHandGameSequencer

ai_betting_player = AIBettingPlayer()
rounds = PokerHandGameSequencer()

# rounds = ManualGameSequencer([InsecureOrderedClient, PlayerShuffleClient, ShuffledPlayerDecryptionClient])
cli, am = CommsClient(rounds, {'betting_player': ai_betting_player}).begin()

print("- [Game Over, {}]".format(time.time()))

# print(dump(cli))
print("~~~~~~~ Game State Log ~~~~~~~~~~")
# print(dump(cli['game'].state_log))
# scriptpath = path.dirname(__file__)
# filename = path.join(scriptpath,
#                      'states/{}_{}.txt'.format(time.time(),
#                                                cli['peer_map'][cli['ident']]['roll']))
#
# with open(filename, 'w') as f:
#     f.write(dump(cli))
#     f.close()
# pass
print(am)
