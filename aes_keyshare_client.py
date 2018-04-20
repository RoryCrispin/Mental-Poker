# coding=utf-8

from cryptography.fernet import Fernet
from yaml import dump, load

from rsa_client import RSAKeyShareClient


class AESKeyshareClient(RSAKeyShareClient):
    """This client handles generating and distributing a shared secret
    AES key. It depends on the players having been ordered (Secure or insecure)
    and that the RSAKeyShare client has been run, and therefore all clients
    have a map of each others public keys."""
    SHARE_SECRET = 'share_secret'
    SHARED_AES_KEY_PARAMS = 'shared_aes_key_params'

    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state, max_players)
        self.queue_map.extend([(self.SHARE_SECRET, self.recv_secret)])
        self.shared_aes_key = None
        self.aes_key_params = None

    def if_am_master_player(self):
        return self.peer_map.get(self.cli.ident).get('roll') == 0

    def alert_all_keys_recvd(self):
        if self.if_am_master_player():
            keyparams = self.generate_aes_key()
            self.aes_key_params = keyparams
            print("I am master, sharing secret...")
            self.send_rsa_broadcast(self.SHARE_SECRET, dump(keyparams).encode())

    def generate_aes_key(self):
        key = Fernet.generate_key()
        self.shared_aes_key = Fernet(key)
        return key

    def is_round_over(self):
        return self.shared_aes_key is not None

    def get_final_state(self):
        state = super().get_final_state()
        state.update({self.SHARED_AES_KEY_PARAMS: self.aes_key_params})
        self.cli.start_encrypting_communication_with_key(aes_key=self.shared_aes_key)
        return state

    def recv_secret(self, data):
        message = data['data']['message']
        decrypted_message = self.key.decrypt(message)
        key = load(decrypted_message)
        self.aes_key_params = key
        self.shared_aes_key = Fernet(key)
