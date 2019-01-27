# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, TypeVar, Union

if TYPE_CHECKING:  # pragma: no cover
    from dry_monads.either import Either  # noqa: Z435, F401
    from dry_monads.primitives.monad import Monad  # noqa: Z435, F401

# We need to have this ugly type because there is no other way around it:
MonadType = TypeVar('MonadType', bound=Union['Monad', 'Either'])
