# coding=utf-8
from uuid import uuid4

import redis
from yaml import load, dump


class RedisClient:
    BLOCK_SIZE = 16
    def __init__(self, channel):
        self.ident = str(uuid4())
        self.channel = channel
        self.r = redis.StrictRedis(decode_responses=True)
        self.p = self.r.pubsub(ignore_subscribe_messages=True)
        self.p.subscribe(channel)
        self.queue = []
        self.do_encrypt_communication = False

    def post_message(self, to=None, m_code=None, data=None):
        return self.r.publish(self.channel,
                              dump({
                                  "sender_id": self.ident,
                                  "to": to,
                                  "m_code": m_code,
                                  "data": self.marshall_data(data),
                                  "encrypted": self.do_encrypt_communication
                              }))

    def marshall_data(self, data):
        dumped_data = dump(data)
        if self.do_encrypt_communication:
            encrypted_data = self.fernet_key.encrypt(dumped_data.encode())
            return encrypted_data
        else:
            return dumped_data

    def unmarshall_data(self, data):
        pass

    def start_encrypting_communication_with_key(self, fernet_key):
        self.do_encrypt_communication = True
        self.fernet_key = fernet_key

    def decode_message(self, message: dict):
        payload = load(message['data'])
        if payload['encrypted']:
            decrypted_message = self.fernet_key.decrypt(payload['data'])
            payload['data'] = load(decrypted_message)
        else:
            payload['data'] = load(payload['data'])
        return payload

