from Client import GameClient
from DHServer import DHServer

from cryptography.hazmat.primitives.serialization\
    import load_pem_public_key

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization\
    import load_pem_parameters, load_pem_public_key
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from DHServer import DHServer
from FernetServer import FernetServer


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
                'type':
                'fernet_message',
                'ciphertext':
                self.fernet.encrypt_message("Hello from client: {}".format(
                    self.cli.ident))
            })

    def recv_encrypted_message(self, data):
        message = data.get('ciphertext')
        print("Secret message recv: {}".format(message))

        print("Decrypted message: {}".format(
            self.fernet.decrypt_message(message)))
