# -*- coding: utf-8 -*-

from returns.io import IO, io_squash


def test_io_squash():
    """Tests that squash works correctly."""
    assert io_squash(
        IO('a'), IO('b'),
    ) == IO(('a', 'b'))

    assert io_squash(
        IO(1), IO(2), IO(3),
    ) == IO((1, 2, 3))

    assert io_squash(
        IO(1), IO(2), IO('3'), IO(4),
    ) == IO((1, 2, '3', 4))
