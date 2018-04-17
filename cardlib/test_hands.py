# coding=utf-8
import pytest

from cardlib.Card import Card, Rank, Face
from cardlib.Hands import HandEnum, HandRank

cAoH = Card(Rank.Ace, Face.Heart)
cKoS = Card(Rank.King, Face.Spade)
cKoD = Card(Rank.King, Face.Diamond)
cKoH = Card(Rank.King, Face.Heart)
cJoD = Card(Rank.Jack, Face.Diamond)
cToD = Card(Rank.Ten, Face.Diamond)
c9oD = Card(Rank.Nine, Face.Diamond)
c8oD = Card(Rank.Eight, Face.Diamond)
c7oS = Card(Rank.Seven, Face.Spade)
c7oH = Card(Rank.Seven, Face.Heart)
c6oS = Card(Rank.Six, Face.Spade)
c5oS = Card(Rank.Five, Face.Spade)
c4oS = Card(Rank.Four, Face.Spade)
c3oS = Card(Rank.Three, Face.Spade)
cAoS = Card(Rank.Ace, Face.Spade)
c6oC = Card(Rank.Six, Face.Club)
c4oD = Card(Rank.Four, Face.Diamond)
c2oS = Card(Rank.Two, Face.Spade)

high_hand = [cAoH, c7oS, c8oD, cKoH, c9oD]
pair_hand = [cAoH, cKoD, c8oD, cKoH, c9oD]
two_pair_hand = [cAoH, cKoD, cKoH, c8oD, c8oD]
set_hand = [cKoS, cKoD, cKoH, c8oD, c7oS]
boat_hand = [cKoS, cKoD, cKoH, c8oD, c8oD]
quad_hand = [cAoH, cAoH, cAoH, cAoH, c8oD]
straight_hand = [c6oC, c7oS, c5oS, c8oD, c9oD]
flush_hand = [cKoS, cAoS, c5oS, c6oS, c7oS]
sf_hand = [c3oS, c4oS, c5oS, c6oS, c7oS]

# Inferior hands
i_high_hand = [cKoS, c7oS, c8oD, c4oS, c9oD]
i_pair_hand = [c6oC, cKoD, c8oD, cKoH, c9oD]
i_two_pair_hand = [c6oC, cKoD, cKoH, c8oD, c8oD]
i_set_hand = [cKoS, cKoD, cKoH, c6oC, c7oS]
i_boat_hand = [cKoS, cKoD, cKoH, c7oS, c7oH]
i_quad_hand = [cAoH, cAoH, cAoH, cAoH, c6oC]
i_straight_hand = [c6oC, c7oS, c5oS, c8oD, c4oD]
i_flush_hand = [cKoS, cAoS, c5oS, c6oS, c4oS]
i_sf_hand = [c3oS, c4oS, c5oS, c6oS, c2oS]

# Other hands
oversize_sf_hand = [c3oS, c4oS, c6oC, c5oS, c6oS, c4oD, c7oS]


@pytest.mark.parametrize(
    "expected_hand,in_hand",
    [(HandEnum.High, high_hand),
     (HandEnum.Pair, pair_hand),
     (HandEnum.TwoPair, two_pair_hand),
     (HandEnum.Set, set_hand),
     (HandEnum.Boat, boat_hand),
     (HandEnum.Quads, quad_hand),
     (HandEnum.Straight, straight_hand),
     (HandEnum.StraightFlush, sf_hand)])
def test_getHand(expected_hand, in_hand):
    assert HandRank.getHand(in_hand).getEnum() == expected_hand


@pytest.mark.parametrize(
    "hand,inf,enum",
    [(high_hand, i_high_hand, HandEnum.High),
     (pair_hand, i_pair_hand, HandEnum.Pair),
     (two_pair_hand, i_two_pair_hand, HandEnum.TwoPair),
     (set_hand, i_set_hand, HandEnum.Set),
     (boat_hand, i_boat_hand, HandEnum.Boat),
     (quad_hand, i_quad_hand, HandEnum.Quads),
     (straight_hand, i_straight_hand, HandEnum.Straight),
     (flush_hand, i_flush_hand, HandEnum.Flush),
     (sf_hand, i_sf_hand, HandEnum.StraightFlush)])
def test_cmp_hands(hand, inf, enum):
    assert HandRank.getHand(hand) > \
           HandRank.getHand(inf)


def test_pair():
    assert hand_checker(HandRank.getPair, pair_hand)
    assert not hand_checker(HandRank.getPair, high_hand)


def test_two_pair():
    assert hand_checker(HandRank.getTwoPair, two_pair_hand)
    assert not hand_checker(HandRank.getTwoPair, high_hand)


def test_set():
    assert hand_checker(HandRank.getSet, set_hand)
    assert hand_checker(HandRank.getSet, set_hand).getEnum() == HandEnum.Set
    assert not hand_checker(HandRank.getSet, high_hand)


def test_boat():
    assert hand_checker(HandRank.get_boat, boat_hand)
    assert not hand_checker(HandRank.get_boat, set_hand)


def test_quads():
    assert hand_checker(HandRank.get_quads, quad_hand)
    assert hand_checker(HandRank.get_quads, quad_hand).get_kickers() == \
           [Rank.Ace, Rank.Eight]
    assert not hand_checker(HandRank.get_quads, high_hand)


def test_straight():
    assert hand_checker(HandRank.getStraight, straight_hand)


def test_flush():
    assert (hand_checker(HandRank.get_flush, flush_hand))


def test_straight_flush():
    assert hand_checker(HandRank.getStraightFlush, sf_hand)


def test_select():
    assert HandRank.select_hand(oversize_sf_hand).getEnum() == HandEnum.StraightFlush


def hand_checker(test_func, hand):
    return test_func(hand)


def test_sequential_cmp():
    assert HandRank.getHand(i_high_hand) < \
           HandRank.getHand(high_hand) < \
           HandRank.getHand(i_pair_hand) < \
           HandRank.getHand(pair_hand) < \
           HandRank.getHand(i_two_pair_hand) < \
           HandRank.getHand(two_pair_hand) < \
           HandRank.getHand(i_set_hand) < \
           HandRank.getHand(set_hand) < \
           HandRank.getHand(i_straight_hand) < \
           HandRank.getHand(straight_hand) < \
           HandRank.getHand(i_flush_hand) < \
           HandRank.getHand(flush_hand) < \
           HandRank.getHand(i_boat_hand) < \
           HandRank.getHand(boat_hand) < \
           HandRank.getHand(i_quad_hand) < \
           HandRank.getHand(quad_hand) < \
           HandRank.getHand(i_sf_hand) < \
           HandRank.getHand(sf_hand)


def test_get_winning_pot():
    pass
