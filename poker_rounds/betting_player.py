# coding=utf-8
import os
from random import choice, randint

import yaml

from poker_rounds.poker_game import BettingCodes, PokerPlayer


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


# pragma: no cover
class HumanBettingPlayer:
    """ This betting player class interrupts play to offer the
    user a choice of which move to make"""
    @staticmethod
    def get_move(game_round, possible_moves, max_bet):
        input_move, bet = None, None
        HumanBettingPlayer.print_game_state(game_round)
        input_move = HumanBettingPlayer.get_move_from_user(possible_moves)
        if input_move == BettingCodes.BET:
            bet = HumanBettingPlayer.get_bet(max_bet)
        return (input_move, bet)

    @staticmethod
    def print_game_state(game_round):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("~~~~~~~~~[ Poker Game ]~~~~~~~~~~")
        print(yaml.dump(game_round.game.state_log))
        HumanBettingPlayer.print_player_states(game_round)

    # pragma: no cover
    @staticmethod
    def get_move_from_user(possible_moves):
        accepted_move = False
        while not accepted_move:
            input_move = input(
                "Chose move from set: {}\n".format(
                    set(possible_moves)))
            for move in possible_moves:
                if move.find(input_move) != -1 and input_move != "":
                    print("Accepted move: {}".format(move))
                    return move
            else:
                print("Move not in list")

    # pragma: no cover
    @staticmethod
    def get_bet(max_bet):
        while True:
            input_bet = input("How much to bet? Max={}".format(max_bet))
            try:
                input_bet = int(input_bet)
            except ValueError:
                pass
            if type(input_bet) == int:
                if input_bet <= max_bet:
                    return input_bet
                print("Invalid input, please retry")

    @staticmethod
    def print_player_states(game_round):
        print(" ==[  Players ]==")
        for ident, player in game_round.peer_map.items():
            if ident == game_round.player.ident:
                print('You >> ', end='')
            print(player[PokerPlayer.POKER_PLAYER])
