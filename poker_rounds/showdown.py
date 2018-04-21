# coding=utf-8
from cardlib.Hands import HandRank
from poker_rounds.poker_game import PokerWords, PokerPlayer, fresh_deck, \
    PokerGame
from secure_decryption_client import DeckDecryptionClient


class ShowdownDeckDecryptor(DeckDecryptionClient):
    SHOWDOWN_REVEAL = 'showdown_reveal'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)

    def get_final_state(self):
        self.fully_decrypt_deck()
        state = super().get_final_state()

        self.update_cryptodeck_with_decrypted_values(state)
        self.populate_showdown_reveal_cards(state)
        self.populate_all_player_hands(state[PokerWords.CRYPTODECK_STATE])
        self.check_original_deck_was_valid(self.deck_state)
        poker_players = self.get_list_of_poker_players(state)
        table_cards = self.get_table_cards(state)
        self.determine_winnings(poker_players, table_cards)
        state.update({PokerWords.DECK_STATE: self.deck_state,
                      'poker_players': poker_players,
                      'table_cards': table_cards})

        return state

    @staticmethod
    def get_table_cards(state):
        return [card.get_card() for card in state[PokerWords.CRYPTODECK_STATE]
                if card.dealt_to is not None and card.dealt_to < 0]

    @staticmethod
    def get_list_of_poker_players(state):
        return [x[1][PokerPlayer.POKER_PLAYER]
                for x in state['peer_map'].items()]

    def update_cryptodeck_with_decrypted_values(self, state):
        i = 0
        for card in self.deck_state:
            state[PokerWords.CRYPTODECK_STATE][i].showdown_decrypt(card)
            i += 1

    @staticmethod
    def check_original_deck_was_valid(deck):
        assert sorted(deck) == fresh_deck

    def populate_showdown_reveal_cards(self, state):
        for card in state[PokerWords.CRYPTODECK_STATE]:
            if card.dealt_to is not None and card.dealt_to < \
                    0 and not card.has_been_dealt:
                state.get('game').state_log.append(
                    {self.SHOWDOWN_REVEAL: str(card.get_card())})

    def populate_all_player_hands(self, crypto_deck):
        for card in crypto_deck:
            if card.dealt_to is not None and card.dealt_to >= 0:
                peer = self.get_peer_at_position(card.dealt_to)[1]
                peer[PokerPlayer.POKER_PLAYER].hand.append(card.get_card())

    @staticmethod
    def get_pots(poker_players):
        return [(x, x.cash_in_pot) for x in poker_players if x.cash_in_pot > 0]

    def determine_winnings(self, poker_players, table_cards):

        while len(self.get_invested_players(poker_players)) > 1:
            current_pot = 0
            minimum_pot = min([x[1] for x in self.get_pots(poker_players)])
            invested_players = self.get_invested_players(poker_players)
            for player, _ in self.get_invested_players(poker_players):
                player.cash_in_pot -= minimum_pot
                current_pot += minimum_pot
            # Get best hand from invested players
            winner = [self.get_winner(
                [x[0] for x in invested_players], table_cards)][0][0]
            winner.winnings += current_pot
        if len(self.get_invested_players(poker_players)) == 1:
            player = self.get_invested_players(poker_players)[0][0]
            player.winnings += player.cash_in_pot
            player.cash_in_pot = 0

        self.update_game_state_log_with_winnings(poker_players)

    def update_game_state_log_with_winnings(self, poker_players):
        for player in poker_players:
            if player.winnings > 0:
                self.state['game'].state_log.append(
                    {PokerGame.ACTION: PokerWords.WINNINGS,
                     'ident': player.ident,
                     PokerWords.WINNINGS: player.winnings})

    # TODO: add support for draws!
    @staticmethod
    def get_winner(list_of_players, table_cards):
        hands = [(player, player.hand + table_cards)
                 for player in list_of_players if not player.folded]
        decoded_hands = [(x[0], HandRank.getHand(x[1])) for x in hands]
        sorted_hands = sorted(decoded_hands, key=lambda x: x[1], reverse=True)
        return sorted_hands[0]

    @staticmethod
    def get_invested_players(poker_players):
        return [(x, x.cash_in_pot)
                for x in poker_players
                if x.cash_in_pot > 0]
