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
