# coding=utf-8
from random import choice, randint

from poker_rounds.poker_game import BettingCodes


class AIBettingPlayer:
    """ This simplistic betting player class simulates a human player
    by making random moves at each opportunity"""
    @staticmethod
    def get_move(game_round, possible_moves, max_bet):
        move = choice(possible_moves)
        bet_size = 0
        if move == BettingCodes.BET:
            bet_size = randint(1, max_bet)
        return (move, bet_size)

