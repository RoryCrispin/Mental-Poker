# coding=utf-8
import yaml
from time import time

from game_sequencer import GameSequencer
from ordered_turn_client import InsecureOrderedClient
from poker_rounds.betting_round_client import BettingClient
from poker_rounds.open_card_reveal_client import OpenCardRevealClient
from poker_rounds.poker_setup import PokerSetup
from poker_rounds.showdown import ShowdownDeckDecryptor
from secure_player_ordering import ShuffledPlayerDecryptionClient, PlayerShuffleClient


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
    DEBUG_TIMINGS = False

    def __init__(self):
        super().__init__()
        from poker_rounds.card_reveal_client import CardRevealClient, HandDecoder
        from poker_rounds.secure_deck_shuffle import DeckShuffleClient

        self.round_order = {
            InsecureOrderedClient: False,
            PlayerShuffleClient: False,
            ShuffledPlayerDecryptionClient: False,
            DeckShuffleClient: False,
            CardRevealClient: False,
            HandDecoder: False,
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
        self.timestamps = []

    def advance_to_next_round(self, cli, state=None):
        self.update_round_completion_list(state)
        for client, complete in self.round_order.items():
            if not complete:
                if self.DEBUG_TIMINGS:
                    self.timestamps.append([client.__name__, time()])
                    print(yaml.dump(self.timestamps))
                next_round = client(cli, state)
                next_round.init_state()
                if next_round.is_round_over():
                    return self.advance_to_next_round(
                        cli, next_round.get_final_state())
                else:
                    return next_round
        next_round = self.get_betting_reveal_state(state)
        if next_round is not None:
            if self.DEBUG_TIMINGS:
                self.timestamps.append([next_round.__name__, time()])
                print(yaml.dump(self.timestamps))
            next_round = next_round(cli, state)
            next_round.init_state()
            return next_round

    @staticmethod
    def has_deck_been_shuffled(state):
        return state.get('crypto_deck_state') is not None

    @staticmethod
    def have_finished_dealing(state):
        finished_dealing = True
        for card in state.get('crypto_deck_state'):
            if card.dealt_to is None:
                break
            if card.dealt_to >= 0 and card.has_been_dealt is False:
                finished_dealing = False
                break
            if card.dealt_to < 0 and card.has_been_dealt is False:
                break
        return finished_dealing

    @staticmethod
    def hand_has_been_decoded(state):
        return state.get('hand') is not None

    def update_round_completion_list(self, state):
        from poker_rounds.secure_deck_shuffle import DeckShuffleClient
        if state is None:
            return
        if not self.round_order[InsecureOrderedClient]:
            self.round_order[InsecureOrderedClient] = True
            return InsecureOrderedClient

        if not self.round_order[PlayerShuffleClient]:
            self.round_order[PlayerShuffleClient] = True
            return PlayerShuffleClient

        if not self.round_order[ShuffledPlayerDecryptionClient]:
            self.round_order[ShuffledPlayerDecryptionClient] = True
            return ShuffledPlayerDecryptionClient

        if self.has_deck_been_shuffled(state):
            self.round_order[DeckShuffleClient] = True
            from poker_rounds.card_reveal_client import CardRevealClient, HandDecoder
            self.round_order[CardRevealClient] = self.have_finished_dealing(state)
            self.round_order[HandDecoder] = self.hand_has_been_decoded(state)
            self.round_order[PokerSetup] = PokerSetup.have_built_poker_player_map(state)

    def get_betting_reveal_state(self, state):
        for round_name, complete in self.betting_round_order.items():
            if not complete:
                only_one_player_left = state.get('num_folded_players') is not None \
                                       and state.get('num_folded_players') == (state.get('max_players') - 1)

                no_active_players = state.get('num_active_players') is not None \
                                    and state.get('num_active_players') == 0

                if only_one_player_left or no_active_players:
                    if not self.betting_round_order.get(self.SHOWDOWN):
                        self.betting_round_order.update({self.SHOWDOWN: True})
                        return self.betting_round_map.get(self.SHOWDOWN)
                    else:
                        return None
                self.betting_round_order.update({round_name: True})
                return self.betting_round_map.get(round_name)
