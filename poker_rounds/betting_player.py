# coding=utf-8
import os
from random import choice

import yaml


class AIBettingPlayer:
    """ This simplistic betting player class simulates a human player
    by making random moves at each opportunity"""
    @staticmethod
    def get_move(game_round, possible_moves):
        return choice(possible_moves)


# pragma: no cover
class HumanBettingPlayer:
    """ This betting player class interrupts play to offer the
    user a choice of which move to make"""
    @staticmethod
    def get_move(game_round, possible_moves):
        os.system('cls' if os.name == 'nt' else 'clear')
        move = None
        print(yaml.dump(game_round.game.state_log))
        accepted_move = False
        while not accepted_move:
            move = input(
                "Chose move from set: {}\n".format(
                    set(possible_moves)))
            if move in possible_moves:
                print("Accepted move")
                accepted_move = True
            else:
                print("Move not in list")
        return move
