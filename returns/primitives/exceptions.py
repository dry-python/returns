# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from returns.primitives.types import MonadType  # noqa: Z435, F401


class UnwrapFailedError(Exception):
    """Raised when a monad can not be unwrapped into a meaningful value."""

    def __init__(self, monad: 'MonadType') -> None:
        """
        Saves halted monad in the inner state.

        So, this monad can later be unpacked from this exception
        and used as a regular value.
        """
        super().__init__()
        self.halted_monad = monad


class ImmutableStateError(Exception):
    """Raised when a monad is forced to be mutated."""
