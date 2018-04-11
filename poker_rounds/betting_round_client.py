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


class BettingClient(TurnTakingClient):
    BET_AMOUNT = 'bet_amount'

    def __init__(self, cli, state=None, max_players=3, start_cash=100):
        self.player: PokerPlayer = None
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(BettingCodes.FOLD, self.handle_fold),
                               (BettingCodes.CALL, self.handle_call),
                               (BettingCodes.BET, self.handle_bet)
                               ])
        self.initial_moves_from = []
        self.game: PokerGame

    def init_blind_bets(self):
        self.cli.log(LogLevel.VERBOSE, "Init Blinds")
        # TODO: we skip the first player because of next TODO
        bigb: PokerPlayer = self.get_peer_at_position(1)[1][PokerPlayer.POKER_PLAYER]
        bigb.set_blind(big_blind=True)

        lilb: PokerPlayer = self.get_peer_at_position(2)[1][PokerPlayer.POKER_PLAYER]
        lilb.set_blind(big_blind=False)

    def alert_players_have_been_ordered(self):
        self.game: PokerGame = self.state['game']
        self.init_blind_bets()
        self.player = self.peer_map[self.cli.ident][PokerPlayer.POKER_PLAYER]
        if self.is_my_turn():
            self.take_turn()

    def take_turn(self):
        if not self.player.folded:
            self.initial_moves_from.append(self.cli.ident)

            if self.player.folded or self.player.allin:
                self.make_skip()
                self.end_my_turn()
                return

            # The extremely smart poker 'AI' follows...
            move_choice = [
                BettingCodes.CALL * 10,
                BettingCodes.BET * 5,
                BettingCodes.FOLD * 100,
            ]
            next_move = choice(move_choice)

            if next_move is BettingCodes.CALL:
                self.make_call()
            elif next_move is BettingCodes.BET:
                self.make_bet(randint(1, 5))
            elif next_move is BettingCodes.FOLD:
                self.make_fold()
        self.end_my_turn()

    def make_skip(self):
        print("Skipping move")
        self.send_round_message(BettingCodes.SKIP, {})

    def make_fold(self):
        self.apply_fold(self.player)

    def apply_fold(self, player: PokerPlayer):
        player.folded = True

    def make_call(self):
        self.cli.log(LogLevel.INFO, "Making Call")
        self.send_round_message(BettingCodes.CALL, {})
        self.apply_call(self.player)

    def make_bet(self, amount: int):
        self.cli.log(LogLevel.INFO, "Making bet of {}".format(amount))
        self.apply_bet(self.player, amount)
        self.send_round_message(BettingCodes.BET, {self.BET_AMOUNT: amount})

    def apply_call(self, player):
        self.game.state_log.append({PokerGame.FROM: player.ident,
                                    PokerGame.ACTION: BettingCodes.CALL})
        player.add_to_pot(self.cash_needed_for_call(player))

    def cash_needed_for_call(self, player):
        max_pot_size = max(self.get_active_pots())
        return max_pot_size - player.cash_in_pot

    def apply_bet(self, player: PokerPlayer, bet_raise: int):
        self.game.state_log.append({PokerGame.FROM: player.ident,
                                    PokerGame.ACTION: BettingCodes.BET,
                                    'raise': bet_raise})
        bet_amount = bet_raise + self.cash_needed_for_call(player)
        return player.add_to_pot(bet_amount)

    def is_round_over(self):
        active_pots = self.get_active_pots()
        all_pots_equal = all([p == active_pots[0] for p in active_pots])
        all_players_moved = len(self.initial_moves_from) >= self.max_players # TODO: We should filter initial_moves to
        # TODO: unique idents only.
        over = all_players_moved and all_pots_equal
        if over:
            print("======================================")
        return over

    def get_active_pots(self):
        active_pots = []
        player: PokerPlayer
        for _, peer in self.peer_map.items():
            player = peer[PokerPlayer.POKER_PLAYER]
            if player.folded:
                break
            active_pots.append(player.cash_in_pot)
        return active_pots

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
            player.folded = True
            self.cli.log(LogLevel.INFO, "Player {} folds".format(player.ident))

    def handle_bet(self, data):
        player: PokerPlayer = self.get_player_from_turn_message(data)
        if self.is_turn_valid(data):
            self.initial_moves_from.append(player.ident)
            amount = data['data'][self.BET_AMOUNT]
            self.apply_bet(player, amount)
            self.cli.log(LogLevel.INFO, "Player {} bets {}".format(player.ident, amount))

    def handle_skip(self, data):
        if self.is_turn_valid():
            print("Got skip from {}".format(data[self.SENDER_ID]))
            pass

    def is_turn_valid(self, data):
        if super().is_turn_valid(data):
            return True
            #TODO: Check for all in/folded players making illegal moves

    def get_player_from_turn_message(self, data) -> PokerPlayer:
        return self.peer_map[data[self.SENDER_ID]][PokerPlayer.POKER_PLAYER]

    def get_final_state(self):
        state = super().get_final_state()
        state.update({'betting_run': True})
        return state
