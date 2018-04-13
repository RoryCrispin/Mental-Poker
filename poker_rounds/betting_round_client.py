from random import randint

from client_logging import LogLevel
from poker_rounds.betting_player import AIBettingPlayer
from poker_rounds.poker_game import PokerGame, PokerPlayer
from turn_taking_client import TurnTakingClient


class BettingCodes():
    CALL = 'call'
    BET = 'bet'
    FOLD = 'fold'
    ALLIN = 'all_in'
    SKIP = 'skip'
    BIG_BLIND = 'big_blind'
    SMALL_BLIND = 'small_blind'


class BettingClient(TurnTakingClient):
    BET_AMOUNT = 'bet_amount'

    def __init__(self, cli, state=None, max_players=3):
        self.player: PokerPlayer = None
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(BettingCodes.FOLD, self.handle_fold),
                               (BettingCodes.CALL, self.handle_call),
                               (BettingCodes.BET, self.handle_bet),
                               (BettingCodes.SKIP, self.handle_skip),
                               (BettingCodes.ALLIN, self.handle_all_in)
                               ])
        self.game: PokerGame

        if self.cli.round_args.get('betting_player') is None:
            self.betting_player = AIBettingPlayer()
            # raise ValueError
        else:
            self.betting_player = self.cli.round_args.get('betting_player')

    def init_blind_bets(self):
        # Clear blind flag:
        for _, player in self.peer_map.items():
            player[PokerPlayer.POKER_PLAYER].reset_blind_flag()

        self.cli.log(LogLevel.VERBOSE, "Init Blinds")
        dealer_position = self.game.dealer
        self.game.advance_to_next_dealer()
        self.cli.log(LogLevel.VERBOSE, "Dealer is {}".format(dealer_position))

        big_blind_played = False
        small_blind_played = False

        for i in range(dealer_position + 1, dealer_position + self.max_players + 1):
            ident, player_map = self.get_peer_at_position(i)
            player = player_map[PokerPlayer.POKER_PLAYER]
            if not player.is_all_in() and not player.folded:
                if not big_blind_played:
                    player.set_blind(self.cli.log, big_blind=True)
                    big_blind_played = True
                elif not small_blind_played:
                    player.set_blind(self.cli.log, big_blind=False)
                    small_blind_played = True

    def alert_players_have_been_ordered(self):
        self.game: PokerGame = self.state['game']
        self.init_blind_bets()
        self.player = self.peer_map[self.cli.ident][PokerPlayer.POKER_PLAYER]
        if self.is_my_turn() and not self.is_round_over():
            self.take_turn()

    def get_possible_moves_for_player(self, player: PokerPlayer):
        possible_moves = []
        if self.player.folded or self.player.is_all_in():
            possible_moves.append(BettingCodes.SKIP)
        else:
            possible_moves.append(BettingCodes.ALLIN)
            possible_moves.append(BettingCodes.FOLD)
            if player.cash_in_hand == self.cash_needed_for_call(player):
                possible_moves.append(BettingCodes.ALLIN)
                possible_moves.append(BettingCodes.FOLD)
            if player.cash_in_hand > self.cash_needed_for_call(player):
                # We make calling more likely TODO: remove
                possible_moves.append(BettingCodes.CALL)
                possible_moves.append(BettingCodes.CALL)
                possible_moves.append(BettingCodes.CALL)
                if self.get_max_raise(player) > 0:
                    possible_moves.append(BettingCodes.BET)
        return possible_moves

    def get_max_raise(self, player: PokerPlayer):
        return player.cash_in_hand - self.cash_needed_for_call(player) - 1

    def take_turn(self):
        possible_moves = self.get_possible_moves_for_player(self.player)
        next_move = self.betting_player.get_move(possible_moves)

        if next_move is BettingCodes.CALL:
            self.make_call()
        elif next_move is BettingCodes.BET:
            self.make_bet(randint(1, self.get_max_raise(self.player)))
        elif next_move is BettingCodes.FOLD:
            self.make_fold()
        elif next_move is BettingCodes.ALLIN:
            self.make_all_in()
        elif next_move is BettingCodes.SKIP:
            self.make_skip()
        else:
            self.cli.log(LogLevel.ERROR, "No move generated!")
        self.end_my_turn()

    def get_current_turn(self):
        current_turn_index = (self.game.dealer + 2 + self.current_turn) % self.max_players
        for ident, peer in self.peer_map.items():
            if peer.get('roll') == current_turn_index:
                return ident
        raise IndexError

    def make_all_in(self):
        self.cli.log(LogLevel.INFO, "I go all in")
        self.send_round_message(BettingCodes.ALLIN, {})
        self.apply_all_in(self.player)

    def make_bet(self, amount: int):
        self.cli.log(LogLevel.INFO, "Making bet of {}".format(amount))
        self.apply_bet(self.player, amount)
        self.send_round_message(BettingCodes.BET, {self.BET_AMOUNT: amount})

    def make_call(self):
        self.cli.log(LogLevel.INFO, "Making Call")
        self.send_round_message(BettingCodes.CALL, {})
        self.apply_call(self.player)

    def make_fold(self):
        self.cli.log(LogLevel.INFO, "I Fold")
        self.send_round_message(BettingCodes.FOLD, {})
        self.apply_fold(self.player)

    def make_skip(self):
        self.send_round_message(BettingCodes.SKIP, {})

    def apply_all_in(self, player: PokerPlayer):
        self.game.state_log.append({PokerGame.FROM: player.ident,
                                    PokerGame.ACTION: BettingCodes.ALLIN})
        self.game.new_raise()
        return player.add_to_pot(player.cash_in_hand)

    def apply_bet(self, player: PokerPlayer, bet_raise: int):
        self.game.state_log.append({PokerGame.FROM: player.ident,
                                    PokerGame.ACTION: BettingCodes.BET,
                                    'raise': bet_raise})
        self.game.new_raise()
        bet_amount = bet_raise + self.cash_needed_for_call(player)
        return player.add_to_pot(bet_amount)

    def apply_call(self, player):
        self.game.state_log.append({PokerGame.FROM: player.ident,
                                    PokerGame.ACTION: BettingCodes.CALL})
        player.last_raise_i_have_called = self.game.last_raise
        player.add_to_pot(self.cash_needed_for_call(player))

    def apply_fold(self, player: PokerPlayer):
        self.game.state_log.append({PokerGame.FROM: player.ident,
                                    PokerGame.ACTION: BettingCodes.FOLD})
        player.folded = True

    def handle_all_in(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.cli.log(LogLevel.INFO, "Got All In from {}".format(player.ident))
            self.apply_all_in(player)

    def handle_bet(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            amount = data['data'][self.BET_AMOUNT]
            self.apply_bet(player, amount)
            self.cli.log(LogLevel.INFO, "Player {} bets {}".format(player.ident, amount))

    def handle_call(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.apply_call(player)
            self.cli.log(LogLevel.INFO, 'Player {} calls'.format(player.ident))

    def handle_fold(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.apply_fold(player)
            self.cli.log(LogLevel.INFO, "Player {} folds".format(player.ident))

    def handle_skip(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.cli.log(LogLevel.INFO, "Got skip from {}".format(data[self.SENDER_ID]))

    def cash_needed_for_call(self, player):
        try:
            max_pot_size = max(self.get_unfolded_pots())
            cash_needed = max_pot_size - player.cash_in_pot
            # print("need to call :: {}".format(cash_needed))
            if cash_needed < 0:
                raise ValueError
            return cash_needed

        except ValueError:
            self.cli.log(LogLevel.ERROR, "No active pots!")
            return None

    def is_round_over(self):
        # TODO: Get rid of all_players_moved
        all_players_called_last_raise = self.all_active_players_have_called_last_raise()
        one_unfolded_player = len(self.get_folded_players()) == (self.max_players - 1)
        if all_players_called_last_raise or one_unfolded_player:
            self.cli.log(LogLevel.INFO, "End of betting round")
            if self.get_peer_at_position(0)[0] == self.cli.ident:
                self.send_round_message(self.LEAVE_ROOM, {})
            return True
        return False

    def get_unfolded_pots(self):
        unfolded = set(self.get_every_player()) - set(self.get_folded_players())
        return [p.cash_in_pot for p in unfolded]

    def get_active_players(self) -> [PokerPlayer]:
        return list((set(self.get_every_player())
                     - set(self.get_folded_players()))
                    - set(self.get_all_in_players()))

    def get_folded_players(self):
        folded_players = []
        player: PokerPlayer
        for player in self.get_every_player():
            if player.folded:
                folded_players.append(player)
        return folded_players

    def get_all_in_players(self):
        all_in_players = []
        player: PokerPlayer
        for player in self.get_every_player():
            if player.is_all_in():
                all_in_players.append(player)
        return all_in_players

    def get_active_pots(self):
        active_pots = []
        player: PokerPlayer
        for player in self.get_every_player():
            if not player.folded and not player.is_all_in():
                active_pots.append(player.cash_in_pot)
        return active_pots

    def get_all_pots(self):
        return [player.cash_in_hand for player in self.get_every_player()]

    def get_every_player(self):
        players = []
        for _, peer in self.peer_map.items():
            player = peer[PokerPlayer.POKER_PLAYER]
            players.append(player)
        return players

    def is_turn_valid(self, data):
        if super().is_turn_valid(data):
            return True
            # TODO: Check for all in/folded players making illegal moves

    def all_active_players_have_called_last_raise(self):
        return all([player.last_raise_i_have_called == self.game.last_raise
                    for player in self.get_active_players()])

    def players_have_called_last_raise(self):
        return [player.last_raise_i_have_called == self.game.last_raise
                for player in self.get_active_players()]

    def get_player_from_turn_message(self, data) -> PokerPlayer:
        return self.peer_map[data[self.SENDER_ID]][PokerPlayer.POKER_PLAYER]

    def get_final_state(self):
        state = super().get_final_state()
        state.update({'max_players': self.max_players,
                      'betting_run': True,
                      'num_active_players': len(self.get_active_players()),
                      'num_folded_players': len(self.get_folded_players())})
        return state
