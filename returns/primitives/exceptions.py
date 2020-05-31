from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from returns.primitives.container import BaseContainer  # noqa: WPS433


class UnwrapFailedError(Exception):
    """Raised when a container can not be unwrapped into a meaningful value."""

    def __init__(self, container: 'BaseContainer') -> None:
        """
        Saves halted container in the inner state.

        So, this container can later be unpacked from this exception
        and used as a regular value.
        """
        super().__init__()
        self.halted_container = container


class ImmutableStateError(AttributeError):
    """
    Raised when a container is forced to be mutated.

    It is a sublclass of ``AttributeError`` for two reasons:

    1. It seems kinda reasonable to expect ``AttributeError``
       on attribute modification
    2. It is used inside ``typing.py`` this way,
       we do have several typing features that requires that behaviour

    See: https://github.com/dry-python/returns/issues/394
    """
