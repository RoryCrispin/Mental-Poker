# coding=utf-8
from uuid import uuid4

from client import LogLevel
from ordered_turn_client import SecureOrderedClient


class TurnTakingClient(SecureOrderedClient):
    END_TURN = 'end_turn'
    ROOM_CODE = 'room_code'
    LEAVE_ROOM = 'leave_room'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.END_TURN, self.recv_end_turn),
                               (self.LEAVE_ROOM, self.recv_leave_room)])
        self.current_turn = 0
        # Pregrnerate a room code; this will be overwritten if we're not player
        # 0
        self.room_code = uuid4()
        self.setup_finished = False

    def recv_leave_room(self, data):
        if self.is_turn_valid(data):
            pass

    def recv_end_turn(self, data):
        # TODO: Assert from correct player
        # The issue causing incorr ect turn synchronisation -> Not clearing the queue buffer between rounds, left over
        # messages need to be deleted

        # TODO: This is common place where the game stops running turns
        if data['data'][self.ROOM_CODE] == self.room_code:
            if not data[self.SENDER_ID] == self.get_current_turn():
                self.cli.log(LogLevel.ERROR,
                             "An invalid turn was made: {}".format(data))
            else:
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
        self.current_turn += 1
        self.cli.post_message(data={self.MESSAGE_KEY: self.END_TURN,
                                    self.ROOM_CODE: self.room_code})

    def take_turn(self):
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
                raise ValueError("Invalid Message")
        return True

    def send_round_message(self, key, data):
        data.update({self.MESSAGE_KEY: key,
                     self.ROOM_CODE: self.room_code})
        self.cli.post_message(data=data)

    def get_ident_at_position(self, position):
        ident, _ = self.get_peer_at_position(position)
        return ident

    def get_peer_at_position(self, position, peer_map=None):
        if peer_map is None:
            peer_map = self.peer_map
        return [peer for peer in peer_map.items() if peer[1]['roll'] ==
                position % self.max_players][0]

    def get_my_position(self):
        return self.peer_map[self.cli.ident]['roll']

