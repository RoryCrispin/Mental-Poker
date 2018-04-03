from time import sleep

from client import LogLevel

from ordered_turn_client import InsecureOrderedClient

class TurnTakingClient(InsecureOrderedClient):
    END_TURN='end_turn'
    def __init__(self, cli, max_players=3):
        super().__init__(cli, max_players)
        self.queue_map.extend([(self.END_TURN, self.recv_end_turn)])
        self.current_turn = 0

    def recv_end_turn(self, _):
        # TODO: Assert from correct player
        self.current_turn += 1
        self.take_turn_if_mine()

    def alert_players_have_been_ordered(self):
        if self.is_my_turn():
            self.take_turn()

    def is_my_turn(self):
        return self.get_current_turn() == self.cli.ident

    def get_current_turn(self):
        for ident, dict in self.peer_map.items():
            if dict.get('roll') == self.current_turn % (self.max_players):
                return ident
        raise IndexError

    def end_my_turn(self):
        self.current_turn += 1
        self.cli.post_message(data={self.MESSAGE_KEY: self.END_TURN})

    def take_turn(self):
        raise NotImplementedError

    def handle_turn(self, data):
        raise NotImplementedError

    def take_turn_if_mine(self):
        if self.is_my_turn():
            self.take_turn()

class CountingClient(TurnTakingClient):
    NEW_COUNT= 'new_count'
    def __init__(self, cli, max_players=3):
        super().__init__(cli, max_players)
        self.queue_map.extend([(self.NEW_COUNT, self.handle_count)])
        self.counting_state = 0

    def take_turn(self):
        self.cli.log(LogLevel.INFO, "Sending move %s" % self.counting_state)
        self.cli.post_message(data={self.MESSAGE_KEY: self.NEW_COUNT,
                                    self.NEW_COUNT: self.counting_state})
        self.end_my_turn()

    def handle_count(self, data):
        self.counting_state = (data['data'][self.NEW_COUNT])
        self.cli.log(LogLevel.INFO, "Received move %s" % self.counting_state)
        self.counting_state += 1

    def is_game_over(self):
        return False
