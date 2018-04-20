# coding=utf-8
import time

from aes_keyshare_client import AESKeyshareClient
from client import CommsClient
from client import GreetingCli
from game_sequencer import ManualGameSequencer
from ordered_turn_client import InsecureOrderedClient
from poker_rounds.betting_player import AIBettingPlayer
from poker_rounds.poker_sequencer import PokerHandGameSequencer

ai_betting_player = AIBettingPlayer()
rounds = PokerHandGameSequencer()
rounds = ManualGameSequencer([InsecureOrderedClient, AESKeyshareClient, GreetingCli])

# rounds = ManualGameSequencer([InsecureOrderedClient, PlayerShuffleClient, ShuffledPlayerDecryptionClient])
cli = CommsClient(rounds, {'betting_player': ai_betting_player}).begin()

print("- [Game Over, {}]".format(time.time()))

# print(dump(cli))
# print("~~~~~~~ Game State Log ~~~~~~~~~~")
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
