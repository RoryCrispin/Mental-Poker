from uuid import uuid4

from yaml import load, dump
import redis
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization\
    import load_pem_parameters, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.serialization import Encoding,\
    ParameterFormat, PublicFormat


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
                    # print(payload)
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


class DFEKeyExchange(GameClient):
    def __init__(self, cli):
        super().__init__(cli)
        self.dh_server = DHServer()
        self.send_initiate()

    def apply_queue(self, queue):
        new_queue = []
        for e in queue:
            data = e.get('data')
            if data.get('dh_begin'):
                self.send_params()
                self.send_pubkey()

            elif data.get('dh_step') == 'params':
                self.handle_params(data)
                self.send_pubkey()

            elif data.get('dh_step') == 'share_pub':
                self.recv_pubkey(data)

            elif data.get('type') == 'fernet_message':
                self.recv_encrypted_message(data)

            else:
                new_queue.append(e)
        return (self, new_queue)

    def send_initiate(self):
        print("Sending init")
        self.cli.post_message(data={'dh_begin': True})

    def handle_params(self, e):
        print("handle params")
        self.dh_server.parse_parameters(e.get('dh_params'))

    def send_params(self):
        print("Sending params")
        params = self.dh_server.get_serialised_parameters()
        self.cli.post_message(data={'dh_step': 'params', 'dh_params': params})

    def send_pubkey(self):
        print("Sending pubkey")
        self.cli.post_message(
            data={
                'dh_step':
                'share_pub',
                'pub':
                self.dh_server.get_public_key().public_bytes(
                    Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
            })

    def recv_pubkey(self, data):
        peerpub = load_pem_public_key(
            data['pub'].encode(), backend=default_backend())
        self.dh_server.submit_public_key(peerpub)
        print(self.dh_server._shared_key)
        self.fernet = FernetServer(self.dh_server._shared_key)

        print("Shared key = {}".format(self.fernet.key))

        self.cli.post_message(
            data={
                'type': 'fernet_message',
                'ciphertext': self.fernet.encrypt_message("Hello from client: {}".format(self.cli.ident))
            })

    def recv_encrypted_message(self, data):
        message = data.get('ciphertext')
        print("Secret message recv: {}".format(message))

        print("Decrypted message: {}".format(
            self.fernet.decrypt_message(message)))


from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class FernetServer():
    def __init__(self, shared_key):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'salt',
            iterations=100000,
            backend=default_backend())
        self.key = base64.urlsafe_b64encode(kdf.derive(shared_key))

        self.f = Fernet(self.key)

    def encrypt_message(self, message):
        return self.f.encrypt(message.encode())

    def decrypt_message(self, cipher):
        return self.f.decrypt(cipher).decode()


class DHServer(object):
    def __init__(self):
        super().__init__()
        # This example DH server uses a known safe prime, or can generate its
        # own if the PEM file is not available.
        # The safe prime used here is ffdhe2048, described here:
        # https://tools.ietf.org/html/rfc7919#appendix-A.1
        # There is nothing strictly wrong with generating your own prime,
        # but this one is well tested.

        import os.path
        pem_path = os.path.join(os.path.dirname(__file__), 'dh_params.pem')
        if not os.path.isfile(pem_path):
            # No PEM file available, generate a new prime of 2048 bits.
            parameters = dh.generate_parameters(
                generator=2, key_size=2048, backend=default_backend())
            s = parameters.parameter_bytes(Encoding.PEM, ParameterFormat.PKCS3)
            with open('dh_params.pem', 'wb') as outfile:
                outfile.write(s)
        # Load PEM file - a standard format for cryptographic
        # keys and numbers.
        with open(pem_path, 'r') as f:
            self.pem_data = f.read().encode("UTF-8")
        self.parse_parameters(self.pem_data.decode())

    def encrypt_message(self, message):
        if not self._shared_key:
            return None
        message = message.encode()
        from os import urandom
        nonce = urandom(16)

        cipher = Cipher(
            algorithms.AES(self._shared_key),
            modes.CTR(nonce),
            backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(bytes([b + 12 % 255 for b in message
                                             ])) + encryptor.finalize()
        return nonce + ciphertext

    def parse_parameters(self, params):
        # TODO: Use proper library serialisation
        # https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/#cryptography.hazmat.primitives.serialization.load_pem_parameters
        bytestring = params.encode()
        self.parameters = load_pem_parameters(
            data=bytestring, backend=default_backend())

    # Return DH parameters (prime and generator)
    def get_serialised_parameters(self):
        return self.pem_data.decode()

    # Generate a new private key (a random number) and produce the public
    # key based on this and the parameters.
    def get_public_key(self):
        self.privatekey = self.parameters.generate_private_key()
        self.public_key = self.privatekey.public_key()
        return self.public_key

    # Receive another public key as part of a handshake, and use it to
    # calculate a share secret
    def submit_public_key(self, pk):
        if pk == None:
            return

        self._pre_master_secret = self.privatekey.exchange(pk)

        # Derive the key
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'g53sec',
            backend=default_backend())

        self._shared_key = hkdf.derive(self._pre_master_secret)


