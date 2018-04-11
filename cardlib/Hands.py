from enum import IntEnum
from itertools import combinations
from itertools import groupby

from src.card import utils


class HandEnum(IntEnum):
    High = 0
    Pair = 1
    TwoPair = 2
    Set = 3
    Straight = 4
    Flush = 5
    Boat = 6
    Quads = 7
    StraightFlush = 8


class Hand:
    def __init__(self, enum, kickers):
        self.enum = enum
        self.kickers = kickers

    def getEnum(self):
        return self.enum

    def getKickers(self):
        return self.kickers

    def __lt__(self, other):
        return (self.getEnum(), self.getKickers()) < \
               (other.getEnum(), other.getKickers())

    def __gt__(self, other):
        return (self.getEnum(), self.getKickers()) > \
               (other.getEnum(), other.getKickers())


class HandRank():
    def getGroupings(cards):
        clist = sorted(cards, key=lambda c: c.rank)
        groups = []
        for face, group in groupby(clist, lambda c: c.rank):
            num = sum(1 for _ in group)
            groups.append((face, num))
        return sorted(groups, key=lambda tup: (tup[1], tup[0]), reverse=True)

    def sortCards(cards, reverse=False):
        return sorted(cards, key=lambda Card: Card.rank, reverse=reverse)

    def flatten_groups_to_faces(groups):
        return [f[0] for f in groups]

    def getHandFromGroupings(groupings):
        zg = groupings
        funcs = [("Quads", HandRank.getQuads), ("Boat", HandRank.getBoat),
                 ("Set", HandRank.getSet), ("2 Pair", HandRank.getTwoPair),
                 ("Pair", HandRank.getPair)]
        for f in funcs:
            print(f[0] + "\t" + str(f[1](zg)))

    def getStraightFlush(cards):
        if (HandRank.getStraight(cards) is not None) & \
                (HandRank.getFlush(cards) is not None):
            return Hand(HandEnum.StraightFlush, HandRank.sortCards(cards))
        else:
            return None

    def getFlush(cards):
        combs = 0
        for i in groupby(cards, lambda Card: Card.face):
            combs += 1
        if combs == 1:
            return Hand(HandEnum.Flush, HandRank.sortCards(cards))
        else:
            return None

    def getStraight(cards):
        cards = HandRank.sortCards(cards)
        if utils.is_list_sequential([int(i) for i in cards]):
            return Hand(HandEnum.Straight, cards)
        else:
            return None

    def getQuads(cards):
        groupings = HandRank.getGroupings(cards)
        if len(HandRank.getPairs(groupings, minSize=4)) >= 1:
            return Hand(HandEnum.Quads, HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    def getBoat(cards):
        # This function doesn't add kickers for hands >= 5 cards
        # It ought to for scalability
        try:
            groupings = HandRank.getGroupings(cards)
            trips = next(filter(lambda x: x[1] == 3, groupings))
            dubs = next(filter(lambda x: x[1] == 2, groupings))
            return Hand(HandEnum.Boat, [trips, dubs])
        except StopIteration:
            return None

    def getSet(cards):
        groupings = HandRank.getGroupings(cards)
        sets = HandRank.getPairs(groupings, minSize=3)
        if len(sets) >= 1:
            return Hand(HandEnum.Set, HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    def getTwoPair(cards):
        groupings = HandRank.getGroupings(cards)
        if len(HandRank.getPairs(groupings)) >= 2:
            return Hand(HandEnum.TwoPair, HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    def getPair(cards):
        groupings = HandRank.getGroupings(cards)
        if len(HandRank.getPairs(groupings)) >= 1:
            return Hand(HandEnum.Pair, HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    def getHigh(cards):
        return Hand(HandEnum.High, HandRank.sortCards(cards))

    def getPairs(groupings, minSize=2):
        return list(filter(lambda x: x[1] >= minSize, groupings))

    def getHand(cards):
        handOrd = [(HandRank.getStraightFlush, HandEnum.StraightFlush),
                   (HandRank.getQuads, HandEnum.Quads),
                   (HandRank.getBoat, HandEnum.Boat),
                   (HandRank.getFlush, HandEnum.Flush),
                   (HandRank.getStraight, HandEnum.Straight),
                   (HandRank.getSet, HandEnum.Set),
                   (HandRank.getTwoPair, HandEnum.TwoPair),
                   (HandRank.getPair, HandEnum.Pair),
                   (HandRank.getHigh, HandEnum.High)]
        return next((x[0](cards) for x in handOrd if x[0](cards) is not None))

    def select_hand(cards, hand_size=5):
        possible_hands = list(combinations(cards, hand_size))
        return max([HandRank.getHand(x) for x in possible_hands])
