# -*- coding: utf-8 -*-

import pytest

from returns.primitives.container import Container


def test_abstract_class():
    """Ensures that Container can not be instanciated."""
    with pytest.raises(TypeError):
        Container(1)  # type: ignore
