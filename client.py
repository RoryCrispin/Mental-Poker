from random import uniform
from time import sleep

from pkr_logging import LogLevel
from redis_client import RedisClient


class Client(RedisClient):
    def __init__(self, round_list):
        super().__init__('poker_chan')
        self.round_list_index = 0
        self.round_list = round_list
        self.queue = []
        self.logged_messages = []
        self.log(LogLevel.INFO, "I am client: {}".format(self.ident))
        self.game = round_list[0](self)
        self.game.init_state()

    def begin(self):
        for message in self.p.listen():
            if message['type'] == 'message':
                payload = RedisClient.decode_message(message)

                if self.message_is_for_me(payload):
                    self.queue.append(payload)
                    self.game, self.queue, self.final_state =\
                        self.game.apply_queue(self.queue)
                    if self.game is None:
                        self.log(LogLevel.VERBOSE, "Round Complete")
                        self.game = self.advance_to_next_round()
                        self.queue = []
                        if self.game is None:
                            return self.final_state
            sleep(uniform(0.001, 0.01))

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
        self.round_list_index += 1
        if self.round_list_index < len(self.round_list):
            print("Next round")
            next_round = self.round_list[self.round_list_index](self, state=self.final_state)
            next_round.init_state()
            if next_round.is_round_over():
                self.advance_to_next_round()
            else:
                return next_round
        else:
            return None

class GameClient():
    SENDER_ID = 'sender_id'
    MESSAGE_KEY = 'message_key'
    def __init__(self, cli, state=None):
        self.cli = cli
        self.queue_map = []
        self.state = state
    # Takes a Queue of messages and returns a new game class along with
    # a new queue state (With the applied element removed)
    # These games are still impure in that they can freely send messages to
    # other clients through execution
    def init_state(self):
        if self.state is not None:
            self.init_existing_state(self.state)
        else:
            self.init_no_state()

    def apply_queue(self, queue):
        new_queue = []
        for e in queue:
            msg_key = e.get('data').get(self.MESSAGE_KEY)
            did_run_job = False
            for k, f in self.queue_map:
                if msg_key == k:
                    f(e) # TODO: to reject jobs, make this funtion return a Bool!
                    did_run_job = True
                    break
            if not did_run_job:
                new_queue.append(e)
        return (None, None,
                self.get_final_state()) if self.is_round_over() else (
                    self, new_queue, None)

    def init_existing_state(self, state):
        self.cli.log(LogLevel.INFO, "Init with existing state!")

    def init_no_state(self):
        self.cli.log(LogLevel.INFO, "Init with no state!")

    def get_message(self, message):
        pass

    def is_round_over(self):
        return False

    def get_final_state(self):
        print("Getting final state!")
        return {'root_state':True,
                'ident':self.cli.ident}



class GreetingCli(GameClient):
    def __init__(self, cli, greetings_sent=0):
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
            'greetings_sent' : self.greetings_sent,
        })
        return state
