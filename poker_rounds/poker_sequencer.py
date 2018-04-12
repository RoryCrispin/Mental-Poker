from game_sequencer import GameSequencer
from poker_rounds.betting_round_client import BettingClient
from poker_rounds.open_card_reveal_client import OpenCardRevealClient
from poker_rounds.poker_setup import PokerSetup
from secure_decryption_client import ShowdownDeckDecryptor


class PokerHandGameSequencer(GameSequencer):
    SHUFFLE_DECK_PHASE = 'shuffle_deck_phase'
    DEAL_CARD_PHASE = 'deal_card_phase'

    FIRST_BETTING_ROUND = 'first_betting_round'
    FLOP_REVEAL = 'flop_reveal'
    FLOP_REVEAL_TWO = 'flop_reveal_two'
    FLOP_REVEAL_THREE = 'flop_reveal_three'
    SECOND_BETTING_ROUND = 'second_betting_round'
    TURN_REVEAL = 'turn_reveal'
    THIRD_BETTING_ROUND = 'third_betting_round'
    RIVER_REVEAL = 'river_reveal'
    SHOWDOWN = 'showdown'

    def __init__(self):
        super().__init__()
        from poker_rounds.card_reveal_client import CardRevealClient, HandDecoder
        from poker_rounds.secure_deck_shuffle import DeckShuffleClient

        self.round_order = {DeckShuffleClient: False,
                            CardRevealClient: False,
                            HandDecoder: False,  # TODO: Three flop cards, then turn and river
                            PokerSetup: False,
                            }

        self.betting_round_order = {
            self.FIRST_BETTING_ROUND: False,
            self.FLOP_REVEAL: False,
            self.FLOP_REVEAL_TWO: False,
            self.FLOP_REVEAL_THREE: False,
            self.SECOND_BETTING_ROUND: False,
            self.TURN_REVEAL: False,
            self.THIRD_BETTING_ROUND: False,
            self.RIVER_REVEAL: False,
            self.SHOWDOWN: False
        }
        self.betting_round_map = {
            self.FIRST_BETTING_ROUND: BettingClient,
            self.FLOP_REVEAL: OpenCardRevealClient,
            self.FLOP_REVEAL_TWO: OpenCardRevealClient,
            self.FLOP_REVEAL_THREE: OpenCardRevealClient,
            self.SECOND_BETTING_ROUND: BettingClient,
            self.TURN_REVEAL: OpenCardRevealClient,
            self.THIRD_BETTING_ROUND: BettingClient,
            self.RIVER_REVEAL: OpenCardRevealClient,
            self.SHOWDOWN: ShowdownDeckDecryptor
        }

        self.betting_rounds_played = 0
        self.open_cards_revealed = 0
        self.game_over = False

    def advance_to_next_round(self, cli, state=None):
        self.update_round_completion_list(state)
        for client, complete in self.round_order.items():
            if not complete:
                next_round = client(cli, state)
                next_round.init_state()
                if next_round.is_round_over():
                    return self.advance_to_next_round(cli, next_round.get_final_state())
                else:
                    return next_round
        next_round = self.get_betting_reveal_state(state)
        if next_round is not None:
            next_round = next_round(cli, state)
            next_round.init_state()
            return next_round

    def update_round_completion_list(self, state):
        from poker_rounds.secure_deck_shuffle import DeckShuffleClient
        if state is None:
            return
        if state.get('crypto_deck_state') is not None:
            self.round_order[DeckShuffleClient] = True

            # Check if all cards have been dealt yet?
            finished_dealing = True
            for card in state.get('crypto_deck_state'):
                if card.dealt_to is None:
                    break
                if card.dealt_to >= 0 and card.has_been_dealt is False:
                    finished_dealing = False
                    break
                if card.dealt_to < 0 and card.has_been_dealt is False:
                    all_open_cards_dealt = False
                    break
            from poker_rounds.card_reveal_client import CardRevealClient, HandDecoder
            self.round_order[CardRevealClient] = finished_dealing

            # Has hand been decoded
            if state.get('hand') is not None:
                self.round_order[HandDecoder] = True

            # Have run poker setup
            if PokerSetup.have_built_poker_player_map(state):
                self.round_order[PokerSetup] = True

            if state.get('betting_run'):
                self.round_order[BettingClient] = True

    def get_betting_reveal_state(self, state):
        for round_name, complete in self.betting_round_order.items():
            if not complete:
                only_one_player_left = state.get('num_folded_players') is not None \
                                       and state.get('num_folded_players') == (state.get('max_players') - 1)
                no_active_players = state.get('num_active_players') is not None \
                                    and state.get('num_active_players') == 0
                if only_one_player_left or no_active_players:
                    print("only one: {}, no active players: {}".format(only_one_player_left,
                                                                       no_active_players))
                    if not self.betting_round_order.get(self.SHOWDOWN):
                        self.betting_round_order.update({self.SHOWDOWN: True})
                        return self.betting_round_map.get(self.SHOWDOWN)
                    else:
                        return None
                self.betting_round_order.update({round_name: True})
                print("]]]]]]]] Running round {} ]]]]]]]]]]".format(round_name))
                return self.betting_round_map.get(round_name)
