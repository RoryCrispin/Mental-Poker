# coding=utf-8
from cardlib.Card import Card, Face, Rank


def test_init_with_val():
    card = Card(10)
    assert repr(card) == "Queen Heart"


def test_init_manually():
    card = Card(Rank.Queen, Face.Heart)
    assert repr(card) == "Queen Heart"
