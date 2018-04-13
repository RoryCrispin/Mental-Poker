from random import choice


class AIBettingPlayer:
    def get_move(self, possible_moves):
        return choice(possible_moves)
