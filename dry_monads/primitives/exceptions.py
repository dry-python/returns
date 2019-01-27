# -*- coding: utf-8 -*-


class UnwrapFailedError(Exception):
    """Raised when a monad can not be unwrapped into a meaningful value."""

    def __init__(self, monad) -> None:
        """Saves halted monad in the inner state."""
        super().__init__()
        self.halted_monad = monad
