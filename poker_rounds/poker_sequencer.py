from game_sequencer import GameSequencer


class PokerHandGameSequencer(GameSequencer):
    SHUFFLE_DECK_PHASE = 'shuffle_deck_phase'
    DEAL_CARD_PHASE = 'deal_card_phase'

    def __init__(self):
        super().__init__()
        from poker_rounds.card_reveal_client import CardRevealClient, HandDecoder
        from poker_rounds.secure_deck_shuffle import DeckShuffleClient

        self.round_order = {DeckShuffleClient: False,
                            CardRevealClient: False,
                            HandDecoder: False}

    def advance_to_next_round(self, cli, state=None):
        self.update_round_completion_list(state)
        for client, complete in self.round_order.items():
            if not complete:
                next_round = client(cli, state)
                next_round.init_state()
                return next_round

    def update_round_completion_list(self, state):
        from poker_rounds.secure_deck_shuffle import DeckShuffleClient
        if state is None: return
        if state.get('crypto_deck_state') is not None:
            self.round_order[DeckShuffleClient] = True

            # Check if all cards have been dealt yet?
            finished_dealing = True
            for card in state.get('crypto_deck_state'):
                if card.dealt_to is None:
                    break
                if card.dealt_to >=0 and card.has_been_dealt is False:
                    finished_dealing = False
                    break
            print("Finished dealing = {}".format(finished_dealing))
            from poker_rounds.card_reveal_client import CardRevealClient, HandDecoder
            self.round_order[CardRevealClient] = finished_dealing

            # Has hand been decoded
            if state.get('hand') is not None:
                self.round_order[HandDecoder] = True