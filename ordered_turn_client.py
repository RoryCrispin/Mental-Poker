from uuid import uuid4

from client import LogLevel
from identifying_client import IdentifyClient


class InsecureOrderedClient(IdentifyClient):
    """This client implements an insecure ordering protocol in which
    all players publish a random key, and players are ordered based on
    their random keys. It's insecure because players cannot confirm that
    their peers rolls are random. As such it is only acceptable to use this
    for non security critical purposes"""
    ROOM_FULL_ROLL = 'room_full_roll'
    JOIN_MESSAGE = 'join_message'
    ROLL = 'roll'
    PLAYERS_HAVE_BEEN_INSECURE_ORDERED = 'players_have_been_insecure_ordered'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state)
        self.queue_map.extend([(self.JOIN_MESSAGE,
                                self.recv_join_message),
                               (self.ROOM_FULL_ROLL,
                                self.recv_roll)])

        self.max_players = max_players
        self.room_closed = False

    def init_existing_state(self, state):
        super().init_existing_state(state)
        if state.get(self.PLAYERS_HAVE_BEEN_INSECURE_ORDERED):
            self.peer_map = state['peer_map']
            self.players_have_been_insecure_ordered = True
            self.alert_players_have_been_ordered()
        else:
            self.init_no_state(call_super=False)

    def init_no_state(self, call_super=True):
        if call_super:
            super().init_no_state()
        self.cli.post_message(data={'message_key': 'join_message'})
        # Pre-generate the roll
        self.roll = 'roll_' + str(uuid4()) + '_roll'
        self.peer_map[self.cli.ident][self.ROLL] = self.roll
        self.players_have_been_insecure_ordered = False

    def recv_join_message(self, _):
        self.request_idenfity()

    def is_round_over(self):
        return self.players_have_been_insecure_ordered

    def alert_players_have_been_ordered(self):
        pass

    def received_all_rolls(self):
        for _, v in self.peer_map.items():
            if v.get(self.ROLL) is None:
                return False
        return True

    def peer_did_join(self):
        if self.get_num_joined_players() >= self.max_players:
            self.send_random_roll()

    def recv_roll(self, data):
        self.peer_map[data.get(self.SENDER_ID)][self.ROLL] = \
            data['data'][self.ROLL]
        if self.received_all_rolls():
            self.cli.log(LogLevel.VERBOSE, "All peer rolls have been received")
            self.order_players()

    def order_players(self):
        """Take the peer map and replace all roll UUID4s with their equivelant
        decimal position ie 0,1,2,3,4 ordering."""
        player_rolls = []
        for ident, v in self.peer_map.items():
            roll = v['roll']
            player_rolls.append((ident, roll))
        player_rolls = sorted(player_rolls, key=lambda tup: tup[1])
        i = 0
        for ident, _ in player_rolls:
            self.peer_map[ident][self.ROLL] = i
            i += 1
        self.players_have_been_insecure_ordered = True
        # self.cli.log(LogLevel.INFO, "I am player{}".format(0))
        self.alert_players_have_been_ordered()

    def send_random_roll(self):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        self.ROOM_FULL_ROLL,
                                    self.ROLL: self.roll})
        self.cli.log(LogLevel.INFO, "Rolling {}".format(self.roll))

    def get_final_state(self):
        state = super().get_final_state()
        state.update({self.PLAYERS_HAVE_BEEN_INSECURE_ORDERED:
                          self.players_have_been_insecure_ordered})
        return state


class SecureOrderedClient(InsecureOrderedClient):
    """This class extends the client, when initialised all players will
    be ordered into a random 'position' such that we can handle them as
    though they were sitting around a physical table"""
    # TODO: implement
    SHUFFLED_LIST = 'shuffled_list'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.SHUFFLED_LIST, self.recv_shuffled_list)])

    def is_round_over(self):
        pass

    def recv_shuffled_list(self, data):
        pass

    def alert_players_have_been_ordered(self):
        if self.peer_map.get(self.cli.ident).get(self.ROLL) == 0:
            # This is player 0, initiate the shuffle
            pl = self.gen_playerlist()
            shuffle(pl)
            self.cli.post_message(data={self.MESSAGE_KEY: self.SHUFFLED_LIST,
                                        self.SHUFFLED_LIST: pl})

    def gen_playerlist(self):
        return list(self.peer_map.keys())
