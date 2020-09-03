from typing import Callable, TypeVar

from returns.context import RequiresContext
from returns.interfaces.specific.reader import ReaderLike2, ReaderLike3
from returns.primitives.hkt import Kind2, Kind3, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_Reader2Kind = TypeVar('_Reader2Kind', bound=ReaderLike2)
_Reader3Kind = TypeVar('_Reader3Kind', bound=ReaderLike3)


@kinded
def bind_context2(
    container: Kind2[_Reader2Kind, _FirstType, _SecondType],
    function: Callable[
        [_FirstType],
        'RequiresContext[_UpdatedType, _SecondType]',
    ],
) -> Kind2[_Reader2Kind, _UpdatedType, _SecondType]:
    """
    Bind a ``RequiresContext`` returning function over a container.

    .. code:: python

      >>> from returns.methods import bind_context2
      >>> from returns.context import Reader

      >>> def example(argument: int) -> Reader[int, int]:
      ...     return Reader(lambda deps: argument + deps)

      >>> assert bind_context2(Reader.from_value(2), example)(3) == 5

    Note, that this function works with only ``Kind2`` containers
    with ``.bind_context`` method.
    See :class:`returns.primitives.interfaces.specific.reader.ReaderLike2`
    for more info.

    """
    return container.bind_context(function)


@kinded
def bind_context3(
    container: Kind3[_Reader3Kind, _FirstType, _SecondType, _ThirdType],
    function: Callable[
        [_FirstType],
        'RequiresContext[_UpdatedType, _ThirdType]',
    ],
) -> Kind3[_Reader3Kind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a ``RequiresContext`` returning function over a container.

    .. code:: python

      >>> from returns.methods import bind_context3
      >>> from returns.context import Reader, ReaderResult
      >>> from returns.result import Success, Failure

      >>> def example(argument: int) -> Reader[int, int]:
      ...     return Reader(lambda deps: argument + deps)

      >>> assert bind_context3(
      ...     ReaderResult.from_value(2), example,
      ... )(3) == Success(5)
      >>> assert bind_context3(
      ...     ReaderResult.from_failure(2), example,
      ... )(3) == Failure(2)

    Note, that this function works with only ``Kind3`` containers
    with ``.bind_context`` method.
    See :class:`returns.primitives.interfaces.specific.reader.ReaderLike3`
    for more info.

    """
    return container.bind_context(function)


#: Useful alias for :func:`~bind_context3`.
bind_context = bind_context3
