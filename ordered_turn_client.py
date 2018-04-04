from uuid import uuid4
from random import shuffle
from client import GameClient, LogLevel


class IdentifyClient(GameClient):
    """This class extends the GameClient with an IDENTIFY command
    which, when pinged - all player will respond with a pong message.
    it is used to identify all players in a given channel"""
    IDENT_REQ_KEY = 'identify_request'
    IDENT_RESP_KEY = 'identify_response'
    PEER_MAP = 'peer_map'

    def __init__(self, cli):
        super().__init__(cli)
        self.peer_map = {self.cli.ident: {}}
        self.queue_map.extend([(IdentifyClient.IDENT_REQ_KEY,
                                self.recv_identify_request),
                               (IdentifyClient.IDENT_RESP_KEY,
                                self.recv_identify_response)])

    def recv_identify_request(self, _):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        IdentifyClient.IDENT_RESP_KEY})

    def recv_identify_response(self, data):
        self.cli.log(LogLevel.INFO, "Recv identify")
        if data.get(self.SENDER_ID) not in self.peer_map:
            self.cli.log(LogLevel.INFO, "Identify Response!")
            self.peer_map[data.get(self.SENDER_ID)] = {}
            self.peer_did_join()

    def request_idenfity(self):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        IdentifyClient.IDENT_REQ_KEY})
        #Send out your own identity too
        self.recv_identify_request(None)

    def get_final_state(self):
        state = super().get_final_state()
        state.update({
            self.PEER_MAP: self.peer_map
        })
        return state

    def get_num_joined_players(self):
        return len(self.peer_map.keys())

    def peer_did_join(self):
        pass


class InsecureOrderedClient(IdentifyClient):
    """This client implements an insecure ordering protocol in which
    all players publish a random key, and players are ordered based on
    their random keys. It's insecure because players cannot confirm that
    their peers rolls are random. As such it is only acceptable to use this
    for non security critical purposes"""
    ROOM_FULL_ROLL = 'room_full_roll'
    JOIN_MESSAGE = 'join_message'
    ROLL = 'roll'

    def __init__(self, cli, max_players=3):
        super().__init__(cli)
        self.queue_map.extend([(self.JOIN_MESSAGE,
                                self.recv_join_message),
                               (self.ROOM_FULL_ROLL,
                                self.recv_roll)])

        self.cli.post_message(data={'message_key': 'join_message'})
        self.max_players = max_players
        self.room_closed = False
        # Pregenerate the roll
        self.roll = 'roll_' + str(uuid4()) + '_roll'
        self.peer_map[self.cli.ident][self.ROLL] = self.roll
        self.players_have_been_ordered = False

    def recv_join_message(self, _):
        self.request_idenfity()

    def is_game_over(self):
        return self.players_have_been_ordered

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
            print("All rolls recvd")
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
        self.players_have_been_ordered = True
        self.alert_players_have_been_ordered()


    def send_random_roll(self):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        self.ROOM_FULL_ROLL,
                                    self.ROLL: self.roll})
        self.cli.log(LogLevel.INFO, "Rolling {}".format(self.roll))


class SecureOrderedClient(InsecureOrderedClient):
    """This class extends the client, when initialised all players will
    be ordered into a random 'position' such that we can handle them as
    though they were sitting around a physical table"""
    SHUFFLED_LIST = 'shuffled_list'

    def __init__(self, cli, max_players=3):
        super().init(cli, max_players)
        self.queue_map.extend([(self.SHUFFLED_LIST, self.recv_shuffled_list)])

    def is_game_over(self):
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
