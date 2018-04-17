# coding=utf-8
from enum import IntEnum
from itertools import combinations
from itertools import groupby

from cardlib import utils


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

    def get_kickers(self):
        return self.kickers

    def __lt__(self, other):
        return (self.getEnum(), self.get_kickers()) < \
               (other.getEnum(), other.get_kickers())

    def __gt__(self, other):
        return (self.getEnum(), self.get_kickers()) > \
               (other.getEnum(), other.get_kickers())


class HandRank:
    @staticmethod
    def get_groupings(cards):
        clist = sorted(cards, key=lambda c: c.rank)
        groups = []
        for face, group in groupby(clist, lambda c: c.rank):
            num = sum(1 for _ in group)
            groups.append((face, num))
        return sorted(groups, key=lambda tup: (tup[1], tup[0]), reverse=True)

    @staticmethod
    def sortCards(cards, reverse=False):
        return sorted(cards, key=lambda card: card.rank, reverse=reverse)

    @staticmethod
    def flatten_groups_to_faces(groups: list):
        return [f[0] for f in groups]

    @staticmethod
    def getHandFromGroupings(groupings: list):
        zg = groupings
        funcs = [("Quads", HandRank.get_quads), ("Boat", HandRank.get_boat),
                 ("Set", HandRank.getSet), ("2 Pair", HandRank.getTwoPair),
                 ("Pair", HandRank.getPair)]
        for f in funcs:
            print(f[0] + "\t" + str(f[1](zg)))

    @staticmethod
    def getStraightFlush(cards):
        if (HandRank.getStraight(cards) is not None) & \
                (HandRank.get_flush(cards) is not None):
            return Hand(HandEnum.StraightFlush, HandRank.sortCards(cards))
        else:
            return None

    @staticmethod
    def get_flush(cards):
        combs = 0
        for i in groupby(cards, lambda card: card.face):
            combs += 1
        if combs == 1:
            return Hand(HandEnum.Flush, HandRank.sortCards(cards))
        else:
            return None

    @staticmethod
    def getStraight(cards):
        cards = HandRank.sortCards(cards)
        if utils.is_list_sequential([int(i) for i in cards]):
            return Hand(HandEnum.Straight, cards)
        else:
            return None

    @staticmethod
    def get_quads(cards):
        groupings = HandRank.get_groupings(cards)
        if len(HandRank.getPairs(groupings, min_size=4)) >= 1:
            return Hand(HandEnum.Quads,
                        HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    @staticmethod
    def get_boat(cards):
        # This function doesn't add kickers for hands >= 5 cards
        # It ought to for scalability
        try:
            groupings = HandRank.get_groupings(cards)
            trips = next(filter(lambda x: x[1] == 3, groupings))
            dubs = next(filter(lambda x: x[1] == 2, groupings))
            return Hand(HandEnum.Boat, [trips, dubs])
        except StopIteration:
            return None

    @staticmethod
    def getSet(cards):
        groupings = HandRank.get_groupings(cards)
        sets = HandRank.getPairs(groupings, min_size=3)
        if len(sets) >= 1:
            return Hand(
                HandEnum.Set, HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    @staticmethod
    def getTwoPair(cards):
        groupings = HandRank.get_groupings(cards)
        if len(HandRank.getPairs(groupings)) >= 2:
            return Hand(HandEnum.TwoPair,
                        HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    @staticmethod
    def getPair(cards):
        groupings = HandRank.get_groupings(cards)
        if len(HandRank.getPairs(groupings)) >= 1:
            return Hand(HandEnum.Pair,
                        HandRank.flatten_groups_to_faces(groupings))
        else:
            return None

    @staticmethod
    def getHigh(cards):
        return Hand(HandEnum.High, HandRank.sortCards(cards))

    @staticmethod
    def getPairs(groupings: list, min_size=2):
        return list(filter(lambda x: x[1] >= min_size, groupings))

    @staticmethod
    def getHand(cards: list):
        hand_ord = [(HandRank.getStraightFlush, HandEnum.StraightFlush),
                    (HandRank.get_quads, HandEnum.Quads),
                    (HandRank.get_boat, HandEnum.Boat),
                    (HandRank.get_flush, HandEnum.Flush),
                    (HandRank.getStraight, HandEnum.Straight),
                    (HandRank.getSet, HandEnum.Set),
                    (HandRank.getTwoPair, HandEnum.TwoPair),
                    (HandRank.getPair, HandEnum.Pair),
                    (HandRank.getHigh, HandEnum.High)]
        return next((x[0](cards) for x in hand_ord if x[0](cards) is not None))

    @staticmethod
    def select_hand(cards: list, hand_size=5):
        possible_hands = list(combinations(cards, hand_size))
        return max([HandRank.getHand(x) for x in possible_hands])
