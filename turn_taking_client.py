from ordered_turn_client import InsecureOrderedClient

class TurnTakingClient(InsecureOrderedClient):
    END_TURN='end_turn'
    def __init__(self, cli, max_players=3):
        super().init(cli, max_players)
        self.current_turn = 0
        self.queue_map.extend([(self.TURN_MSG, self.handle_turn)])

    def alert_players_have_been_ordered(self):
        if self.is_my_turn():
            self.take_turn()

    def is_my_turn(self):
        return self.get_current_turn() == self.cli.ident

    def get_current_turn(self):
        for ident, dict in self.peer_map:
            if dict.get('roll') == self.current_turn:
                return ident
        raise IndexError

    def end_my_turn(self):
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
        super().init(cli, max_players)
        self.queue_map.extend([(self.NEW_COUNT, self.handle_count)])
        self.count = 0

    def take_turn(self):
        self.cli.post_message(data={self.MESSAGE_KEY: self.NEW_COUNT,
                                    self.NEW_COUNT: self.count})
        self.count += 1

    def handle_count(self, data):
        print(data['data'][self.NEW_COUNT])
        self.take_turn_if_mine()
