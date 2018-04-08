

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


class PokerHandGameSequencer(GameSequencer):
    SHUFFLE_DECK_PHASE = 'shuffle_deck_phase'
    DEAL_CARD_PHASE = 'deal_card_phase'

    def __init__(self):
        super().__init__()
        from card_reveal_client import CardRevealClient
        from secure_deck_shuffle import DeckShuffleClient

        self.round_order = {DeckShuffleClient: False,
                            CardRevealClient: False}

    def advance_to_next_round(self, cli, state=None):
        self.update_round_completion_list(state)
        for client, complete in self.round_order.items():
            if not complete:
                next_round = client(cli, state)
                next_round.init_state()
                return next_round

    def update_round_completion_list(self, state):
        from secure_deck_shuffle import DeckShuffleClient
        if state is None: return
        if state.get('crypto_deck_state') is not None:
            self.round_order[DeckShuffleClient] = True

            # Check if all cards have been dealt yet?
            finished_dealing = True
            for card in state.get('crypto_deck_state'):
                if card.dealt_to is not None and card.has_been_dealt is False:
                    finished_dealing = False
                    break
            print("Finished dealing = {}".format(finished_dealing))
            from card_reveal_client import CardRevealClient
            self.round_order[CardRevealClient] = finished_dealing
