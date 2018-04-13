import os
from random import choice

import yaml


class AIBettingPlayer:
    def get_move(self, round, possible_moves):
        return choice(possible_moves)


class HumanBettingPlayer:
    def get_move(self, round, possible_moves):
        os.system('cls' if os.name == 'nt' else 'clear')

        print(yaml.dump(round.game.state_log))
        accepted_move = False
        while not accepted_move:
            move = input("Chose move from set: {}\n".format(set(possible_moves)))
            if move in possible_moves:
                print("Accepted move")
                accepted_move = True
            else:
                print("Move not in list")
        return move
