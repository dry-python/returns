# -*- coding: utf-8 -*-

from returns.io import IO


def test_io_map():
    """Ensures that IO container supports ``.map()`` method."""
    assert IO(1).map(
        lambda number: number / 2,
    ) == IO(0.5)


def test_io_bind():
    """Ensures that IO container supports ``.bind()`` method."""
    assert IO('a').bind(
        lambda number: IO(number + 'b'),
    ) == IO('ab')
