from cardlib import utils


def test_is_list_sequential():
    good_lists = [
        [1, 2, 3, 4, 5, 6],
        [5, 6, 7, 8, 9],
        [100, 101, 102, 103]
    ]
    bad_lists = [
        [1, 2, 3, 4, 6],
        [6, 5, 4, 3, 2, 1],
        [7, 6, 5, 4, 3]
    ]
    assert all(utils.is_list_sequential(elem)
               for elem in good_lists)
    assert not any(utils.is_list_sequential(elem)
                   for elem in bad_lists)
