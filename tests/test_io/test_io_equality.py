# -*- coding: utf-8 -*-

import pytest

from returns.io import IO


def test_equality():
    """Ensures that containers can be compared."""
    assert IO(1) == IO(1)
    assert str(IO(1)) == '<IO: 1>'
    assert hash(IO(1))


def test_nonequality():
    """Ensures that containers are not compared to regular values."""
    assert IO(1) != 1
    assert IO(1) is not IO(1)
    assert IO(1) != IO(2)
