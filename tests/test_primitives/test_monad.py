# -*- coding: utf-8 -*-

import pytest

from dry_monads.primitives.monad import Monad


def test_abstract_class():
    """Ensures that Monad can not be instanciated."""
    with pytest.raises(TypeError):
        Monad()
