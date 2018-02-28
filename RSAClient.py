from Crypto.PublicKey import RSA

from Client import GameClient, readable_ident, LogLevel


class RSAKeyShareClient(GameClient):
    def __init__(self, cli, max_players=2):
        super().__init__(cli)
        self.player_map = []
        self.max_players = max_players
        self.handshake_message = b'RSA_HANDSHAKE_MESSAGE'
        self.key = RSA.generate(2048)
        self.queue_map = [('rsa_pubkey', self.recv_pubkey),
                          ('rsa_handshake', self.recv_handshake)]
        self.share_my_pubkey()

    def share_my_pubkey(self):
        print("Sharing my pubkey")
        self.cli.post_message(
            data={
                'message_key': 'rsa_pubkey',
                'rsa_pubkey': self.key.publickey().exportKey('PEM').decode()
            })

    def is_game_over(self):
        return len(self.player_map) >= self.max_players

    def recv_pubkey(self, e):
        p_ident = e.get('sender_id')
        p_key = e.get('data').get('rsa_pubkey')
        if self.get_player(p_ident) is None:  # If key not stored
            self.player_map.append((p_ident, p_key))
            self.cli.log(LogLevel.INFO, "Got pubkey from {}".format(
                readable_ident(p_ident)))
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
            data={
                'message_key': 'rsa_handshake',
                'handshake': message,
            })
        self.cli.log(LogLevel.INFO, "Sent handshake to {}".format(
            readable_ident(ident)))

    def recv_handshake(self, e):
        hand = (self.key.decrypt(e.get('data').get('handshake')))
        if hand == self.handshake_message:
            self.cli.log(LogLevel.INFO, "Handshake with {} OK".format(
                readable_ident(e['sender_id'])))
        else:
            self.cli.log(LogLevel.ERROR, "Bad handshake with client {}".format(
                readable_ident(e['sender_id'])))

    def get_player(self, ident):
        for p in self.player_map:
            if p[0] == ident:
                return p
        return None

    def get_final_state(self):
        state = (super(RSAKeyShareClient, self).get_final_state())
        state.append({
            'ident':
            self.cli.ident,
            'pubkey':
            self.key.publickey().exportKey('PEM').decode(),
            'playerlist':
            self.player_map
        })
        return state
