# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, TypeVar, Union

if TYPE_CHECKING:  # pragma: no cover
    from returns.either import Either  # noqa: Z435, F401
    from returns.primitives.monad import Monad  # noqa: Z435, F401

# We need to have this ugly type because there is no other way around it:
MonadType = TypeVar('MonadType', bound=Union['Monad', 'Either'])
