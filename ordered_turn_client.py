from uuid import uuid4
import hashlib
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
        self.peer_map = {self.cli.ident:{}}
        self.queue_map.extend([(IdentifyClient.IDENT_REQ_KEY,
                                self.recv_identify_request),
                               (IdentifyClient.IDENT_RESP_KEY,
                                self.recv_identify_response)])

    def recv_identify_request(self, _):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        IdentifyClient.IDENT_RESP_KEY})

    def recv_identify_response(self, data):
        if data.get(self.SENDER_ID) not in self.peer_map:
            self.cli.log(LogLevel.INFO, "Identify Response!")
            self.peer_map[data.get(self.SENDER_ID)] = {}
            self.peer_did_join()
        else:
            print("NOT NEW")


    def request_idenfity(self):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        IdentifyClient.IDENT_REQ_KEY})

    def get_final_state(self):
        state = super(IdentifyClient, self).get_final_state()
        state.append({
            self.PEER_MAP: self.peer_map
        })
        return state

    def get_num_joined_peers(self):
        return len(self.peer_map.keys())

    def peer_did_join(self):
        pass

class ClosedRoomClient(IdentifyClient):
    """This class waits for a specified number of players
    before proposing a new 'room' in which communication can happen
    This is used to set a table size, await all players joining then
    close off admission, all future clients can then assume that no
    players will join the room mid-session"""
    ROOM_FULL_ROLL = 'room_full_roll'
    JOIN_MESSAGE = 'join_message'
    ROLL = 'roll'
    def __init__(self, cli, max_peers=2):
        super().__init__(cli)
        self.queue_map.extend([(ClosedRoomClient.JOIN_MESSAGE,
                               self.recv_join_message),
                              (ClosedRoomClient.ROOM_FULL_ROLL,
                               self.recv_roll)])

        self.cli.post_message(data={'message_key': 'join_message'})
        self.max_peers = max_peers
        self.room_closed = False
        # Pregenerate the roll
        self.roll = 'roll_' + str(uuid4()) + '_roll'
        self.roll_commitment = hashlib.sha3_256(self.roll.encode()).digest()

    def recv_join_message(self, _):
        self.request_idenfity()

    def is_game_over(self):
        pass

    def received_all_rolls(self):
        for _, v in self.peer_map.items():
            if v.get(self.ROLL) is None:
                return False
        return True

    def get_final_state(self):
        state = (super(ClosedRoomClient, self).get_final_state())
        state.append({
        })
        return state

    def peer_did_join(self):
        if self.get_num_joined_peers() >= self.max_peers:
            self.send_random_roll()

    def recv_roll(self, data):
        self.peer_map[data.get(self.SENDER_ID)][self.ROLL] =\
                                    data['data'][self.ROLL]
        if self.received_all_rolls():
            print("All rolls recvd")
            self.order_players()

    def order_players(self):
        player_rolls = [(self.cli.ident, self.roll)]
        for ident, v in self.peer_map.items():
            roll = v['roll']
            player_rolls.append((ident, roll))
        player_rolls = sorted(player_rolls, key=lambda tup: tup[1])
        i = 0
        for ident, _ in player_rolls:
            self.peer_map[ident][self.ROLL] = i
            i += 1
        pass


    def send_random_roll(self):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                    self.ROOM_FULL_ROLL,
                                    self.ROLL:self.roll})
        self.cli.log(LogLevel.INFO, "Rolling {}".format(self.roll))


class OrderedTurnClient(ClosedRoomClient):
    """This class extends the client, when initialised all players will
    be ordered into a random 'position' such that we can handle them as
    though they were sitting around a physical table"""
    pass
