# -*- coding: utf-8 -*-

from typing import TypeVar, Union

from returns.either import Either  # noqa: F401
from returns.primitives.monad import Monad  # noqa: F401

# We need to have this ugly type because there is no other way around it:
MonadType = TypeVar('MonadType', bound=Union['Monad', 'Either'])
