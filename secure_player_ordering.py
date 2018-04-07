from secure_decryption_client import SecureDecryptionClient
from secure_shuffle_client import SecureShufflingClient


class PlayerShuffleClient(SecureShufflingClient):
    """Use the SecureShuffleClient to securely shuffle a list of the player indexes."""

    def alert_players_have_been_ordered(self):
        print("Setting deck!")
        self.shuffle_state = self.get_player_rolls()
        super().alert_players_have_been_ordered()

    def get_player_rolls(self):
        player_rolls = []
        for _, peer in self.peer_map.items():
            player_rolls.append(peer['roll'] + 10)  # Add 2 because we can't encrypt numbers <= 1
        return player_rolls


class ShuffledPlayerDecryptionClient(SecureDecryptionClient):
    """Take the shuffled list of player indexes from PlayerShuffleClient and rearrange
    the players into these positions, such that the players have now been ordered in a
    fair, random permutation, and that no player has any control over where they're sat"""

    def get_final_state(self):
        state = super().get_final_state()
        self.fully_decrypt_deck()
        # Assign new positions in table.
        new_positions = []
        i = 0
        for new_position in self.deck_state:
            new_position -= 2  # Remove the addition added to keep numbers >= 2 for SRA encryption
            for ident, peer in self.peer_map.items():
                if peer['roll'] == new_position:
                    new_positions.append((ident, i))
                    i += 1
        for ident, position in new_positions:
            self.peer_map[ident]['roll'] = position
        state.update(self.peer_map)
        return state
