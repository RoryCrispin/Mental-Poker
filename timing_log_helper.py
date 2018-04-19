from itertools import tee

from yaml import load

timing_1024 = """
- [InsecureOrderedClient, 1524144868.960126]
- [PlayerShuffleClient, 1524144869.119843]
- [ShuffledPlayerDecryptionClient, 1524144870.509171]
- [DeckShuffleClient, 1524144871.007317]
- [CardRevealClient, 1524144875.7386398]
- [CardRevealClient, 1524144875.8897321]
- [CardRevealClient, 1524144876.0286531]
- [CardRevealClient, 1524144876.144813]
- [CardRevealClient, 1524144876.252424]
- [CardRevealClient, 1524144876.350529]
- [HandDecoder, 1524144876.445238]
- [PokerSetup, 1524144876.44834]
- [BettingClient, 1524144876.450109]
- [OpenCardRevealClient, 1524144876.5071528]
- [OpenCardRevealClient, 1524144876.658941]
- [OpenCardRevealClient, 1524144876.8018591]
- [BettingClient, 1524144876.93534]
- [ShowdownDeckDecryptor, 1524144876.9541602]
- [Game Over, 1524144884.7354429]
"""

timing_2048 = """- [InsecureOrderedClient, 1524137554.476557]
- [PlayerShuffleClient, 1524137554.5404701]
- [ShuffledPlayerDecryptionClient, 1524137560.058912]
- [DeckShuffleClient, 1524137563.093793]
- [CardRevealClient, 1524137585.388269]
- [CardRevealClient, 1524137585.916872]
- [CardRevealClient, 1524137586.666262]
- [CardRevealClient, 1524137587.678771]
- [CardRevealClient, 1524137588.207417]
- [CardRevealClient, 1524137588.4919412]
- [HandDecoder, 1524137589.019768]
- [PokerSetup, 1524137589.025473]
- [BettingClient, 1524137589.033026]
- [OpenCardRevealClient, 1524137589.332382]
- [OpenCardRevealClient, 1524137590.095258]
- [OpenCardRevealClient, 1524137590.8524952]
- [BettingClient, 1524137591.62799]
- [OpenCardRevealClient, 1524137591.645192]
- [BettingClient, 1524137592.396338]
- [ShowdownDeckDecryptor, 1524137592.41613]
- [Game Over, 1524137643.975622]
"""

timing_512 = """- [InsecureOrderedClient, 1524145358.859255]
- [PlayerShuffleClient, 1524145358.889678]
- [ShuffledPlayerDecryptionClient, 1524145359.033447]
- [DeckShuffleClient, 1524145359.1351502]
- [CardRevealClient, 1524145360.062769]
- [CardRevealClient, 1524145360.11617]
- [CardRevealClient, 1524145360.166682]
- [CardRevealClient, 1524145360.201802]
- [CardRevealClient, 1524145360.235497]
- [CardRevealClient, 1524145360.261656]
- [HandDecoder, 1524145360.307701]
- [PokerSetup, 1524145360.310416]
- [BettingClient, 1524145360.313449]
- [OpenCardRevealClient, 1524145360.341068]
- [OpenCardRevealClient, 1524145360.385657]
- [OpenCardRevealClient, 1524145360.42935]
- [BettingClient, 1524145360.485932]
- [ShowdownDeckDecryptor, 1524145360.529116]
- [Game Over, 1524145361.709314]"""


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

""" R command: 
ggplot(timings, aes(color=name))
 + geom_segment(aes(x=started, xend=ended, y=index, yend=index, size=3))
 + geom_text(aes(label=name, x=ended, y=index), check_overlap = TRUE, hjust=FALSE, nudge_x = 3) 
 + theme(legend.position = "none")
 + scale_x_continuous(name="Time Elapsed (s)", limits = c(0,120), breaks = seq(0,120, 15)) 
 + scale_y_continuous(breaks= NULL, name = "") + ggtitle("Timeing diagram for SRA keysize : 2048")
"""
