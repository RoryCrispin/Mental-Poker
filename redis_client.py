# coding=utf-8
import hashlib
from uuid import uuid4

import redis
from Crypto.PublicKey import RSA
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
        self.own_rsa_key = None
        self.peer_rsa_keys = []

    def post_message(self, to=None, m_code=None, data=None):
        marshalled_data, hash = self.marshall_data(data)
        return self.r.publish(self.channel,
                              dump({
                                  "sender_id": self.ident,
                                  "to": to,
                                  "m_code": m_code,
                                  "data": marshalled_data,
                                  "hash": hash,
                                  "encrypted": self.do_encrypt_communication
                              }))

    def marshall_data(self, data):
        dumped_data = dump(data)
        if self.do_encrypt_communication:
            encrypted_data = self.fernet_key.encrypt(dumped_data.encode())
            hashed_data = hashlib.sha224(encrypted_data).hexdigest()
            signed_hash = self.own_rsa_key.sign(hashed_data.encode(), 0)
            return encrypted_data, signed_hash
        else:
            return dumped_data, None

    def start_encrypting_communication_with_key(self, fernet_key):
        self.do_encrypt_communication = True
        self.fernet_key = fernet_key

    def decode_message(self, message: dict):
        payload = load(message['data'])
        if payload['encrypted']:
            assert self.verify_message_signiture(payload)
            decrypted_message = self.fernet_key.decrypt(payload['data'])
            payload['data'] = load(decrypted_message)
        else:
            payload['data'] = load(payload['data'])
        return payload

    def verify_message_signiture(self, payload) -> bool:
        if payload['sender_id'] != self.ident:
            recv_hash = payload['hash']
            gen_hash = hashlib.sha224(payload['data']).hexdigest()
            peer_rsa_key_param = [x for x in self.peer_rsa_keys if x[0] == payload['sender_id']][0][1]
            peer_rsa_key = RSA.importKey(peer_rsa_key_param)
            return peer_rsa_key.verify(gen_hash.encode(), recv_hash)
        else:
            return True
