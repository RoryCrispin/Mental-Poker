from uuid import uuid4
from yaml import load, dump

import redis


class RedisClient():
    def __init__(self, channel):
        self.ident = str(uuid4())
        self.channel = channel
        self.r = redis.StrictRedis(decode_responses=True)
        self.p = self.r.pubsub(ignore_subscribe_messages=True)
        self.p.subscribe(channel)
        self.queue = []

    def post_message(self, to=None, m_code=None, data=None):
        return self.r.publish(self.channel,
                              dump({
                                  "sender_id": self.ident,
                                  "to": to,
                                  "m_code": m_code,
                                  "data": dump(data)
                              }))

    def decode_message(message):
        payload = load(message['data'])
        payload['data'] = load(payload['data'])
        return payload


class Client(RedisClient):
    def __init__(self, initial_game):
        super().__init__('poker_chan')
        self.game = initial_game(self)
        self.queue = []
        self.begin()

    def begin(self):
        self.post_message(data={'hello': True})
        for message in self.p.listen():
            if message['type'] == 'message':
                payload = RedisClient.decode_message(message)

                if payload.get('sender_id') != self.ident:
                    self.queue.append(payload)
                    self.game, self.queue =\
                        self.game.apply_queue(self.queue)


class GameClient():
    def __init__(self, cli):
        self.cli = cli

    # Takes a Queue of messages and returns a new game class along with
    # a new queue state (With the applied element removed)
    # These games are still impure in that they can freely send messages to
    # other clients
    def apply_queue(self, queue):
        return (self, queue)


class GreetingCli(GameClient):
    def __init__(self, cli, greetings_sent=0):
        super().__init__(cli)
        self.greetings_sent = greetings_sent

    def apply_queue(self, queue):
        new_queue = []
        for e in queue:
            if e.get('data').get('hello'):
                self.send_greeting(e)
            else:
                new_queue.append(e)
        return (self, new_queue)

    def send_greeting(self, data):
        self.cli.post_message(data={'Welcome: Player ': self.greetings_sent})
        self.greetings_sent += 1
        yield "Greeting sent!"
