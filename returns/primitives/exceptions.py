# -*- coding: utf-8 -*-


class UnwrapFailedError(Exception):
    """Raised when a monad can not be unwrapped into a meaningful value."""

    def __init__(self, monad):
        """
        Saves halted monad in the inner state.

        So, this monad can later be unpacked from this exception
        and used as a regular value.
        """
        super().__init__()
        self.halted_monad = monad


class ImmutableStateError(Exception):
    """Raised when a monad is forced to be mutated."""
