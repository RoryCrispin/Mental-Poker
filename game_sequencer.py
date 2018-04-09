

class GameSequencer:
    def __init__(self):
        pass

    def advance_to_next_round(self, cli, state=None):
        raise NotImplementedError


class ManualGameSequencer(GameSequencer):
    """ Legacy game sequencer used lots in testing as
    it allows arbitrary lists of rounds to be defined as an
    array - to be sequenced through one by one - allowing for
    isolation of game components so that they can be individually
     tested and debugged."""

    def __init__(self, rounds):
        super().__init__()
        self.rounds = rounds
        self.round_index = 0

    def advance_to_next_round(self, cli, state=None):
        if len(self.rounds) > self.round_index:
            next_round = self.rounds[self.round_index]
            self.round_index += 1
            next_round = next_round(cli, state)
            next_round.init_state()
            return next_round
        return None


