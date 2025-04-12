from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Callable
from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from returns.interfaces.unwrappable import Unwrappable  # noqa: WPS433


_ValueType_co = TypeVar("_ValueType_co", covariant=True)
_FuncParams = ParamSpec("_FuncParams")
_ExceptionType = TypeVar("_ExceptionType", bound=Exception)


class UnwrapFailedError(Exception):
    """Raised when a container can not be unwrapped into a meaningful value."""

    __slots__ = ("halted_container",)

    def __init__(self, container: Unwrappable) -> None:
        """
        Saves halted container in the inner state.

        So, this container can later be unpacked from this exception
        and used as a regular value.
        """
        super().__init__()
        self.halted_container = container

    def __reduce__(self):  # noqa: WPS603
        """Custom reduce method for pickle protocol.

        This helps properly reconstruct the exception during unpickling.
        """
        return (
            self.__class__,  # callable
            (self.halted_container,),  # args to callable
        )


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


def add_note_to_exception(
    exception: _ExceptionType,
    message: bool | str,
    function: Callable[_FuncParams, _ValueType_co],
) -> _ExceptionType:
    """
    A utility function to add a generic note with file name, line number, and
    function name to the exception. If a custom message is provided, it will be
    added as an additional note to the exception.
    """

    if not message:
        return exception

    # If the user provides a custom message, add it as a note
    # to the exception.  Otherwise just add a generic note.
    if isinstance(message, str):
        exception.add_note(message)

    # Add the generic note.
    exc_traceback = exception.__traceback__
    if exc_traceback is None:
        return exception

    if exc_traceback.tb_next is None:
        return exception

    filename = exc_traceback.tb_next.tb_frame.f_code.co_filename
    line_number = exc_traceback.tb_next.tb_lineno
    exception.add_note(
        f"Exception occurred in {function.__name__} "
        f"of {filename} "
        f"at line number {line_number}."
    )

    return exception
