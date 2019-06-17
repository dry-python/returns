# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from returns.primitives.container import Container  # noqa: F401, Z435

_ContainerType = TypeVar('_ContainerType', bound='Container')


class UnwrapFailedError(Exception):
    """Raised when a container can not be unwrapped into a meaningful value."""

    def __init__(self, container: _ContainerType) -> None:
        """
        Saves halted container in the inner state.

        So, this container can later be unpacked from this exception
        and used as a regular value.
        """
        super().__init__()
        self.halted_container = container


class ImmutableStateError(Exception):
    """Raised when a container is forced to be mutated."""
