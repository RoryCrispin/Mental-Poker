# coding=utf-8

from yaml import dump

from client import CommsClient
from poker_rounds.human_betting_player import HumanBettingPlayer
from poker_rounds.poker_sequencer import PokerHandGameSequencer

print("Starting game")
ai_betting_player = HumanBettingPlayer()
rounds = PokerHandGameSequencer()
cli = CommsClient(rounds, {'betting_player': ai_betting_player, 'log_level': 100}).begin()

print("~~~~~~~ Game State Log ~~~~~~~~~~")
print(dump(cli['game'].state_log))
# scriptpath = os.path.dirname(__file__)
# filename = cli['peer_map'][cli['ident']]['roll']
# fila_path = os.path.join(
#     scriptpath, 'states/{}_{}.txt'.format(time.time(), filename))
#
# with open(filename, 'w') as f:
#     f.write(dump(cli))
#     f.close()
# pass
