from random import randint, choice

from client_logging import LogLevel
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
        self.initial_moves_from = []
        self.game: PokerGame

    def init_blind_bets(self):
        # Clear blind flag:
        for _, player in self.peer_map.items():
            player[PokerPlayer.POKER_PLAYER].reset_blind_flag()

        # TODO: Get blind players to skip their first turns
        self.cli.log(LogLevel.VERBOSE, "Init Blinds")
        # TODO: we skip the first player because of next TODO
        dealer_position = self.game.dealer
        self.game.advance_to_next_dealer()
        print("Dealer is {}".format(dealer_position))

        big_blind_played = False
        small_blind_played = False

        # TODO: check if player can afford blind
        for i in range(dealer_position + 1, dealer_position + self.max_players + 1):
            ident, player_map = self.get_peer_at_position(i)
            player = player_map[PokerPlayer.POKER_PLAYER]
            if not player.is_all_in() and not player.folded:
                if not big_blind_played:
                    self.initial_moves_from.append(player.ident)
                    player.set_blind(big_blind=True)
                    big_blind_played = True
                elif not small_blind_played:
                    self.initial_moves_from.append(player.ident)
                    player.set_blind(big_blind=False)
                    small_blind_played = True

    def alert_players_have_been_ordered(self):
        self.game: PokerGame = self.state['game']
        self.init_blind_bets()
        self.player = self.peer_map[self.cli.ident][PokerPlayer.POKER_PLAYER]
        if self.is_my_turn():
            self.take_turn()

    def get_possible_moves(self, player: PokerPlayer):
        possible_moves = []
        if self.player.folded or self.player.is_all_in():
            possible_moves.append(BettingCodes.SKIP)
        else:
            possible_moves.append(BettingCodes.ALLIN)
            possible_moves.append(BettingCodes.FOLD)
            if player.cash_in_hand > self.cash_needed_for_call(player):
                possible_moves.append(BettingCodes.CALL)
                possible_moves.append(BettingCodes.CALL)
                possible_moves.append(BettingCodes.CALL)

                possible_moves.append(BettingCodes.BET)
        return possible_moves

    def get_max_raise(self, player: PokerPlayer):
        return player.cash_in_hand - self.cash_needed_for_call(player) - 1

    def take_turn(self):
        if not self.player.folded:
            self.initial_moves_from.append(self.cli.ident)
            next_move = choice(self.get_possible_moves(self.player))
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
                print(self.get_possible_moves(self.player))
        self.end_my_turn()

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
        print("Skipping move")
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
            self.initial_moves_from.append(player.ident)
            print("Got All In from {}".format(player.ident))
            self.apply_all_in(player)

    def handle_bet(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.initial_moves_from.append(player.ident)
            amount = data['data'][self.BET_AMOUNT]
            self.apply_bet(player, amount)
            self.cli.log(LogLevel.INFO, "Player {} bets {}".format(player.ident, amount))

    def handle_call(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.initial_moves_from.append(player.ident)
            self.apply_call(player)
            self.cli.log(LogLevel.INFO, 'Player {} calls'.format(player.ident))

    def handle_fold(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.initial_moves_from.append(player.ident)
            self.apply_fold(player)
            self.cli.log(LogLevel.INFO, "Player {} folds".format(player.ident))

    def handle_skip(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.initial_moves_from.append(player.ident)
            print("Got skip from {}".format(data[self.SENDER_ID]))

    def cash_needed_for_call(self, player):
        try:
            max_pot_size = max(self.get_unfolded_pots())
            cash_needed = max_pot_size - player.cash_in_pot
            # print("need to call :: {}".format(cash_needed))
            if cash_needed < 0:
                raise ValueError
            return cash_needed

        except ValueError:
            print("No active pots!")
            return None

    def is_round_over(self):
        # TODO: Get rid of all_players_moved
        over = self.all_active_players_have_called_last_raise()
        print("Folded players: {}, All in players: {}, Active players: {}, Called {}"
              .format(len(self.get_folded_players()),
                      len(self.get_all_in_players()),
                      len(self.get_active_players()),
                      self.players_have_called_last_raise()))
        if over:
            print("======================================")
        return over

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
        state.update({'betting_run': True})
        return state
