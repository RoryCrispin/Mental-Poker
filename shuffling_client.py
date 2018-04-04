from turn_taking_client import TurnTakingClient
from client import LogLevel
from random import shuffle

class ShufflingClient(TurnTakingClient):
    SHUFFLE_DECK = 'shuffle_deck'
    def __init__(self, cli, max_players=3):
        super().__init__(cli, max_players)
        self.queue_map.extend([(self.SHUFFLE_DECK, self.recv_shuffle)])
        self.shuffle_state = list(range(1,10))
        self.shuffled_times = 0

    def take_turn(self):
        shuffle(self.shuffle_state)
        self.shuffled_times += 1
        self.cli.log(LogLevel.INFO, "Sent Shuffle")
        self.cli.post_message(data={self.MESSAGE_KEY: self.SHUFFLE_DECK,
                                    self.SHUFFLE_DECK: self.shuffle_state})
        self.end_my_turn()

    def recv_shuffle(self, data):
        self.cli.log(LogLevel.INFO, "Recv Shuffle")
        self.shuffle_state = data['data'][self.SHUFFLE_DECK]
        self.shuffled_times += 1

    def is_game_over(self):
        return self.shuffled_times >= self.max_players

    def get_final_state(self):
        # state = (super(ShufflingClient, self).get_final_state())
        state = super().get_final_state()
        state.update({
            'deck': self.shuffle_state
        })
        return state
