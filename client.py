from redis_client import RedisClient
from pkr_logging import LogLevel

class Client(RedisClient):
    def __init__(self, initial_game):
        super().__init__('poker_chan')
        self.game = initial_game(self)
        self.queue = []
        self.logged_messages = []
        self.log(LogLevel.INFO, "I am client: {}".format(self.ident))

    def begin(self):
        for message in self.p.listen():
            if message['type'] == 'message':
                payload = RedisClient.decode_message(message)

                if self.message_is_for_me(payload):
                    self.queue.append(payload)
                    self.game, self.queue, self.final_state =\
                        self.game.apply_queue(self.queue)
                    if self.game is None:
                        self.log(LogLevel.VERBOSE, "Game Complete")
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

    def log(self, log_level, message):
        self.logged_messages.append((log_level, message))
        print("{} <> {}".format(str(log_level), message))


class GameClient():
    def __init__(self, cli):
        self.cli = cli
        self.queue_map = []

    # Takes a Queue of messages and returns a new game class along with
    # a new queue state (With the applied element removed)
    # These games are still impure in that they can freely send messages to
    # other clients through execution
    def apply_queue(self, queue):
        new_queue = []
        for e in queue:
            msg_key = e.get('data').get('message_key')
            did_run_job = False
            for k, f in self.queue_map:
                if msg_key == k:
                    f(e)
                    did_run_job = True
            if not did_run_job:
                new_queue.append(e)
        return (None, None,
                self.get_final_state()) if self.is_game_over() else (
                    self, new_queue, None)

    def get_message(self, message):
        pass

    def is_game_over(self):
        return False

    def get_final_state(self):
        print("Getting final state!")
        return [{'root_state':True}]


class GreetingCli(GameClient):
    def __init__(self, cli, greetings_sent=0):
        super().__init__(cli)
        self.greetings_sent = greetings_sent
        self.queue_map = [('hello_message', self.send_greeting),
                          ('close_game', self.notify_game_close)]
        self.cli.post_message(data={'message_key': 'hello_message'})
        self.end_game = False

    def is_game_over(self):
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
        state.append({
            'greetings_sent' : self.greetings_sent
        })
        return state