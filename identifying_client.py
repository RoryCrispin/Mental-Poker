from client import GameClient, LogLevel


class IdentifyClient(GameClient):
    """This class extends the GameClient with an IDENTIFY command
    which, when pinged - all player will respond with a pong message.
    it is used to identify all players in a given channel"""
    IDENT_REQ_KEY = 'identify_request'
    IDENT_RESP_KEY = 'identify_response'
    PEER_MAP = 'peer_map'

    def __init__(self, cli, state=None):
        super().__init__(cli, state)
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

    def request_idenfity(self):
        self.cli.log(LogLevel.INFO, "Requesting Identify")
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

    def init_existing_state(self, state):
        super().init_existing_state(state)
        self.peer_map = state['peer_map']

    def init_no_state(self):
        super().init_no_state()
        self.peer_map = {self.cli.ident: {}}

    def get_players(self):
        pass
