from itertools import tee

from yaml import load

timing_2048 = """- [InsecureOrderedClient, 1524229849.785036]
- [FernetKeyshareClient, 1524229849.817926]
- [PlayerShuffleClient, 1524229850.2023869]
- [ShuffledPlayerDecryptionClient, 1524229850.46126]
- [DeckShuffleClient, 1524229850.9347572]
- [CardRevealClient, 1524229855.558521]
- [CardRevealClient, 1524229855.678422]
- [CardRevealClient, 1524229855.8315132]
- [CardRevealClient, 1524229856.012413]
- [CardRevealClient, 1524229856.144419]
- [CardRevealClient, 1524229856.201045]
- [HandDecoder, 1524229856.300716]
- [PokerSetup, 1524229856.303756]
- [BettingClient, 1524229856.306123]
- [OpenCardRevealClient, 1524229856.3852868]
- [OpenCardRevealClient, 1524229856.534813]
- [OpenCardRevealClient, 1524229856.6996841]
- [BettingClient, 1524229856.855969]
- [ShowdownDeckDecryptor, 1524229856.895018]
- [Game Over, 1524229864.594204]"""

# Provided by: https://docs.python.org/3/library/itertools.html#recipes


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


timings = load(timing_2048)
pass

start_time = timings[0][1]

print("name, started, ended, index")
i = 0
for pairs in pairwise(timings):
    round_name = pairs[0][0]
    time_started = pairs[0][1] - start_time
    time_ended = pairs[1][1] - start_time
    print("{}, {}, {}, {}".format(round_name, time_started, time_ended, i))
    i += 1

"""R command 1024: ggplot(dat, aes(color=name)) + geom_segment(aes(x=started,
xend=ended, y=index, yend=index, size=3)) + geom_text(aes(label=name, x=ended,
y=index, size=3), check_overlap = TRUE, hjust=FALSE, nudge_x =0.3) +
theme(legend.position = "none") + scale_x_continuous(name="Time Elapsed (s)",
limits = c(0,19), breaks = seq(0,19, 2)) + scale_y_continuous(breaks= NULL,
name = "") + ggtitle("Timing diagram for SRA keysize : 1024")

"""
