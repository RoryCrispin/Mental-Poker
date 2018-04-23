# coding=utf-8
import click
import time
from yaml import dump

from client import CommsClient
from poker_rounds.betting_player import AIBettingPlayer
from poker_rounds.human_betting_player import HumanBettingPlayer
from poker_rounds.poker_sequencer import PokerHandGameSequencer


@click.command()
@click.option('--log-level', default=100, help='Log level for the client, lower is more logs')
@click.option('--player', default='c', help='Player, (c)omputer or (h)uman')
@click.option('--host', default='localhost', help='Hostname of the redis message broker')
@click.option('--num-players', default=3, help='The number of players to wait for in the game')
def run(log_level, player, host, num_players):
    print(player, num_players)
    if player == 'c':
        betting_player = AIBettingPlayer()
    elif player == 'h':
        betting_player = HumanBettingPlayer()
    else:
        print("Invalid arguments, please specify a player")
        return
    rounds = PokerHandGameSequencer()
    cli = CommsClient(rounds, {'betting_player': betting_player, 'log_level': log_level,
                               'host': host, 'num_players': num_players}).begin()

    print("- [Game Over, {}]".format(time.time()))

    print("~~~~~~~ Game State Log ~~~~~~~~~~")
    print(dump(cli['game'].state_log))
    print("My Ident: %s" % cli['ident'])


if __name__ == '__main__':
    run()
