# -*- coding: utf-8 -*-


class UnwrapFailedError(Exception):
    """Raised when a container can not be unwrapped into a meaningful value."""

    def __init__(self, container):
        """
        Saves halted container in the inner state.

        So, this container can later be unpacked from this exception
        and used as a regular value.
        """
        super().__init__()
        self.halted_container = container


class ImmutableStateError(Exception):
    """Raised when a container is forced to be mutated."""
