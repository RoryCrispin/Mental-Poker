import logging

from client_logging import LogLevel
from game_sequencer import GameSequencer
from redis_client import RedisClient


class CommsClient(RedisClient):
    def __init__(self, game_sequencer: GameSequencer, round_args={}):
        super().__init__('poker_chan')
        self.log_level = 0
        self.round_args = round_args
        self.logger = logging.getLogger("pkr")
        self.round_list_index = 0
        self.game_sequencer = game_sequencer
        self.queue = []
        self.logged_messages = []
        self.log(LogLevel.INFO, "I am client: {}".format(self.ident))
        self.round = game_sequencer.advance_to_next_round(self)

    def begin(self):
        for message in self.p.listen():
            if message['type'] == 'message':
                if message['data'] == 'pdb_start':
                    import ipdb;
                    ipdb.set_trace()
                    break
                if message['data'] == 'dump_game_log':
                    pass
                payload = RedisClient.decode_message(message)
                # print(yaml.dump(payload['data']))
                if self.message_is_for_me(payload):
                    self.queue.append(payload)
                    self.round, self.queue, self.final_state = \
                        self.round.apply_queue(self.queue)
                    if self.round is None:
                        self.log(LogLevel.VERBOSE, "Round Complete")
                        self.round = self.advance_to_next_round()
                        self.queue = []
                        if self.round is None:
                            return self.final_state

    def message_is_for_me(self, payload):
        from_self = payload.get('sender_id') == self.ident
        to_all = payload.get('to') is None
        to_self = payload.get('to') == self.ident
        if from_self:
            return False
        if to_all:
            return True
        if to_self:
            return True
        return False

    def log(self, log_level, message):
        self.logged_messages.append((log_level, message))
        print("{} <> {}".format(str(log_level), message))

    def advance_to_next_round(self):
        return self.game_sequencer.advance_to_next_round(self, self.final_state)


class GameClient():
    SENDER_ID = 'sender_id'
    MESSAGE_KEY = 'message_key'
    IDENT_REQ_KEY = 'identify_request'
    IDENT_RESP_KEY = 'identify_response'
    PEER_MAP = 'peer_map'
    def __init__(self, cli: CommsClient, state=None):
        self.cli = cli
        self.queue_map = []
        self.state = state
        self.previous_state = {}
        self.logger = logging.getLogger("pkr")
        self.queue_map.extend([(self.IDENT_REQ_KEY,
                                self.recv_identify_request),
                               (self.IDENT_RESP_KEY,
                                self.recv_identify_response)])

    # Takes a Queue of messages and returns a new game class along with
    # a new queue state (With the applied element removed)
    # These games are still impure in that they can freely send messages to
    # other clients through execution
    def init_state(self):
        if self.state is not None:
            self.previous_state = self.state
            self.init_existing_state(self.state)
        else:
            self.init_no_state()

    def apply_queue(self, queue):  # -> GameClient, Queue, FinalState
        new_queue = []
        for event in queue:
            msg_key = event.get('data').get(self.MESSAGE_KEY)
            did_run_job = False
            for k, queue_handler_func in self.queue_map:
                if msg_key == k:
                    queue_handler_func(event)
                    did_run_job = True
                    break
            if not did_run_job:
                self.cli.log(LogLevel.ERROR, "Did not run a job with key: {}".format(msg_key))
                new_queue.append(event)
        return (None, None,
                self.get_final_state()) if self.is_round_over() else \
            (self, new_queue, None)

    def init_existing_state(self, state):
        self.cli.log(LogLevel.VERBOSE, "Init round with existing state!")
        self.peer_map = state['peer_map']

    def init_no_state(self):
        self.cli.log(LogLevel.VERBOSE, "Init round with no state!")
        self.peer_map = {self.cli.ident: {}}

    def request_idenfity(self):
        self.cli.log(LogLevel.INFO, "Requesting Identify")
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        self.IDENT_REQ_KEY})
        # Send out your own identity too
        self.recv_identify_request(None)

    def request_idenfity(self):
        self.cli.log(LogLevel.INFO, "Requesting Identify")
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        self.IDENT_REQ_KEY})
        # Send out your own identity too
        self.recv_identify_request(None)

    def recv_identify_response(self, data):
        if data.get(self.SENDER_ID) not in self.peer_map:
            self.cli.log(LogLevel.INFO, "Identify Response!")
            self.peer_map[data.get(self.SENDER_ID)] = {}
            self.peer_did_join()

    def recv_identify_request(self, _):
        self.cli.post_message(data={self.MESSAGE_KEY:
                                        self.IDENT_RESP_KEY})

    def is_round_over(self):
        return False

    def get_final_state(self) -> dict:
        state = self.previous_state
        state.update({'root_state': True,
                      'ident': self.cli.ident,
                      self.PEER_MAP: self.peer_map
                      })
        return state

    def get_num_joined_players(self):
        return len(self.peer_map.keys())




class GreetingCli(GameClient):
    def __init__(self, cli, state=None, greetings_sent=0):
        super().__init__(cli)
        self.greetings_sent = greetings_sent
        self.queue_map.extend([('hello_message', self.send_greeting),
                               ('close_game', self.notify_game_close)])
        self.cli.post_message(data={'message_key': 'hello_message'})
        self.end_game = False

    def is_round_over(self):
        if self.greetings_sent >= 2:
            self.cli.post_message(data={'message_key': 'close_game'})
            return True
        else:
            return self.end_game

    def notify_game_close(self, _):
        self.end_game = True

    def send_greeting(self, data):
        self.cli.post_message(data={'Welcome: Player ': self.greetings_sent})
        self.greetings_sent += 1
        self.cli.log(LogLevel.INFO, "Greetings sent {}".format(
            self.greetings_sent))

    def get_final_state(self):
        state = (super(GreetingCli, self).get_final_state())
        state.update({
            'greetings_sent': self.greetings_sent,
        })
        return state
