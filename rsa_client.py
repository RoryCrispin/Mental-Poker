# coding=utf-8
from Crypto.PublicKey import RSA

from client import GameClient, LogLevel


class RSAKeyShareClient(GameClient):
    def __init__(self, cli, state=None, max_players=3):
        super().__init__(cli, state)
        self.player_map = []
        self.max_players = max_players
        self.handshake_message = b'RSA_HANDSHAKE_MESSAGE'
        self.key = RSA.generate(2048)
        self.cli.own_rsa_key = self.key
        self.queue_map.extend([('rsa_pubkey', self.recv_pubkey),
                               ('rsa_handshake', self.recv_handshake)])
        self.share_my_pubkey()

    def share_my_pubkey(self):
        self.cli.post_message(
            data={
                'message_key': 'rsa_pubkey',
                'rsa_pubkey': self.key.publickey().exportKey('PEM').decode()
            })

    def is_round_over(self):
        return self.all_keys_recvd()

    def all_keys_recvd(self):
        return len(self.player_map) >= self.max_players - 1

    def recv_pubkey(self, e):
        p_ident = e.get('sender_id')
        p_key = e.get('data').get('rsa_pubkey')
        if self.get_player(p_ident) is None:  # If key not stored
            self.player_map.append((p_ident, p_key))
            self.cli.log(LogLevel.INFO, "Got pubkey from {}".format(
                (p_ident)))

            self.share_my_pubkey()
            self.send_handshake(p_ident)

    def send_handshake(self, ident):
        peer_key = self.get_player(ident)[1]
        if peer_key is None:
            self.cli.log(LogLevel.ERROR,
                         "Tried to handshake a nonexistent player")
        peer_key_parse = RSA.importKey(peer_key)
        message = peer_key_parse.encrypt(self.handshake_message, 0)
        self.cli.post_message(
            to=ident,
            m_code=None,
            data={
                'message_key': 'rsa_handshake',
                'handshake': message,
            })
        self.cli.log(LogLevel.INFO, "Sent handshake to {}".format(
            (ident)))

    def alert_all_keys_recvd(self):
        pass

    def recv_handshake(self, e):
        hand = (self.key.decrypt(e.get('data').get('handshake')))
        if hand == self.handshake_message:
            self.cli.log(LogLevel.INFO, "Handshake with {} OK".format(
                (e['sender_id'])))
            if self.all_keys_recvd():
                self.alert_all_keys_recvd()
        else:
            self.cli.log(LogLevel.ERROR, "Bad handshake with client {}".format(
                (e['sender_id'])))

    def get_player(self, ident):
        for p in self.player_map:
            if p[0] == ident:
                return p
        return None

    def get_final_state(self):
        state = (super(RSAKeyShareClient, self).get_final_state())
        state.update({
            'ident':
                self.cli.ident,
            'pubkey':
                self.key.publickey().exportKey('PEM').decode(),
            'playerlist':
                self.player_map
        })
        self.cli.peer_rsa_keys = self.player_map
        return state

    def send_rsa_broadcast(self, message_key, message: bytes):
        """Send a message to all players, encrypted individually with each of
        their public keys"""
        for ident, key in self.player_map:
            if ident != self.cli.ident:
                peer_key = RSA.importKey(key)
                encrypted_message = peer_key.encrypt(message, 0)[0]
                self.cli.post_message(to=ident,
                                      data={
                                          self.MESSAGE_KEY: message_key,
                                          'message': encrypted_message,
                                          'for': ident
                                      })
