# coding=utf-8
from enum import Enum, IntEnum
from itertools import product


class Face(Enum):
    Club = 0
    Diamond = 1
    Heart = 2
    Spade = 3


class Rank(IntEnum):
    Two = 0
    Three = 1
    Four = 2
    Five = 3
    Six = 4
    Seven = 5
    Eight = 6
    Nine = 7
    Ten = 8
    Jack = 9
    Queen = 10
    King = 11
    Ace = 12


class Card:
    def __init__(self, rank, face=None):
        if face is None:
            val = rank
            self.rank = Rank(val % 13)
            self.face = Face(val % 4)
        else:
            self.rank = rank
            self.face = face

    def __repr__(self):
        return "%s %s" % (self.rank.name, self.face.name)

    def __sortkey__(self):
        return self.rank

    def __lt__(self, other):
        return self.rank < other.rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __int__(self):
        return self.rank

    def __add__(self, x):
        return Card(Rank(int(self) + int(x)), self.face)

    def __eq__(self, other):
        return self.face == other.face and self.rank == other.rank


# def generate_full_deck():
#     faces = [Face.Club, Face.Diamond, Face.Spade, Face.Heart]
#     ranks = range(0, 13)
#     return [Card(Rank(x[1]), x[0]) for x in product(faces, ranks)]

def generate_full_deck():
    return [Card(p[0], p[1]) for p in product(Rank, Face)]
