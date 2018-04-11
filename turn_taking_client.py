from uuid import uuid4

from client import LogLevel
from ordered_turn_client import InsecureOrderedClient


class TurnTakingClient(InsecureOrderedClient):
    END_TURN = 'end_turn'
    ROOM_CODE = 'room_code'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.END_TURN, self.recv_end_turn)])
        self.current_turn = 0
        # Pregrnerate a room code; this will be overwritten if we're not player 0
        self.room_code = uuid4()
        self.setup_finished = False

    def recv_end_turn(self, data):
        # TODO: Assert from correct player
        # The issue causing incorr ect turn synchronisation -> Not clearing the queue buffer between rounds, left over
        # messages need to be deleted
        if data['data'][self.ROOM_CODE] == self.room_code:
            self.current_turn += 1
            self.take_turn_if_mine()

    def is_first_turn(self):
        return self.current_turn == 0

    def alert_players_have_been_ordered(self):
        if self.is_my_turn():
            self.take_turn()

    def is_my_turn(self):
        return self.get_current_turn() == self.cli.ident

    def get_current_turn(self):
        for ident, peer in self.peer_map.items():
            if peer.get('roll') == self.current_turn % self.max_players:
                return ident
        raise IndexError

    def end_my_turn(self):
        print("Ending my turn")
        self.current_turn += 1
        self.cli.post_message(data={self.MESSAGE_KEY: self.END_TURN,
                                    self.ROOM_CODE: self.room_code})

    def message_for_this_room(self, room_code):
        return room_code == self.room_code

    def take_turn(self):
        raise NotImplementedError

    def handle_turn(self, data):
        raise NotImplementedError

    def take_turn_if_mine(self):
        if self.is_my_turn():
            self.take_turn()

    def is_turn_valid(self, data):
        if data['data'][self.ROOM_CODE] != self.room_code:
            if self.current_turn == 0:
                self.room_code = data['data'][self.ROOM_CODE]
                return True
            else:
                # This feature is not _fully_ tested. It's intended to block messages form other
                # rooms from causing bugs in new rounds
                self.cli.log(LogLevel.ERROR, "Invalid message")
                return False
        return True

    def send_round_message(self, key, data):
        data.update({self.MESSAGE_KEY: key,
                     self.ROOM_CODE: self.room_code})
        self.cli.post_message(data=data)

    def get_ident_at_position(self, position):
        ident, _ = self.get_peer_at_position(position)
        return ident

    def get_peer_at_position(self, position):
        for ident, peer in self.peer_map.items():
            if peer['roll'] == position % self.max_players:  # Mod with max players so function is cyclic
                return ident, peer
        return None

    def get_my_position(self):
        return self.peer_map[self.cli.ident]['roll']


class CountingClient(TurnTakingClient):
    NEW_COUNT = 'new_count'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.NEW_COUNT, self.handle_count)])
        self.counting_state = 0

    def take_turn(self):
        self.counting_state += 1
        self.cli.log(LogLevel.INFO, "Sending move %s" % self.counting_state)
        self.cli.post_message(data={self.MESSAGE_KEY: self.NEW_COUNT,
                                    self.ROOM_CODE: self.room_code,
                                    self.NEW_COUNT: self.counting_state})
        self.end_my_turn()

    def handle_count(self, data):
        if self.is_turn_valid(data):
            self.counting_state = (data['data'][self.NEW_COUNT])
            self.cli.log(LogLevel.INFO, "Received move %s" % self.counting_state)

    def is_round_over(self):
        return self.counting_state >= 10
