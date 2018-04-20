# coding=utf-8
from uuid import uuid4

import redis
from Crypto.Cipher.AES import AESCipher
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
        self.aes_key: AESCipher = None

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
            encrypted_data = self.aes_key.encrypt(dumped_data.encode())
            print("Encrypting ")
            return encrypted_data
        else:
            print("Not Encrypting ")
            return dumped_data

    def unmarshall_data(self, data):
        pass

    def start_encrypting_communication_with_key(self, aes_key):
        self.do_encrypt_communication = True
        self.aes_key = aes_key

    def decode_message(self, message: dict):
        payload = load(message['data'])
        if payload['encrypted']:
            decrypted_message = self.aes_key.decrypt(payload['data'])
            payload['data'] = load(decrypted_message)
        else:
            payload['data'] = load(payload['data'])
        return payload


class AESRedisClient(RedisClient):
    def set_key(self, aes_key):
        self.aes_key = aes_key

    def post_message(self, to=None, m_code=None, data=None, encrypt=True):
        encrypted_data = None
        pass
