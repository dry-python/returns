# -*- coding: utf-8 -*-

from returns.converters import squash_io
from returns.io import IO


def test_squash_io():
    """Tests that squash works correctly."""
    assert squash_io(
        IO('a'), IO('b'),
    ) == IO(('a', 'b'))

    assert squash_io(
        IO(1), IO(2), IO(3),
    ) == IO((1, 2, 3))

    assert squash_io(
        IO(1), IO(2), IO('3'), IO(4.0),
    ) == IO((1, 2, '3', 4.0))
