from client import GameClient, LogLevel
from crypto.makeRsaKeys import SRA_key

class SRAEncryptionClient(GameClient):
    def __init__(self, cli, max_players=2):
        super.__init__(cli)
        self.max_players = max_players
        self.initial_message = b'SRA_WELCOME_MESSAGE'
        

