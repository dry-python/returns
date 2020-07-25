from typing import Callable, TypeVar

from returns.context import RequiresContext
from returns.interfaces.specific.reader import ReaderBased2, ReaderBased3
from returns.primitives.hkt import Kind2, Kind3, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_Reader2Kind = TypeVar('_Reader2Kind', bound=ReaderBased2)
_Reader3Kind = TypeVar('_Reader3Kind', bound=ReaderBased3)


def internal_bind_context2(
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
    See :class:`returns.primitives.interfaces.specific.reader.ReaderBased2`
    for more info.

    """
    return container.bind_context(function)


#: Kinded version of :func:`~internal_bind_context2`,
#: use it to infer real return type.
bind_context2 = kinded(internal_bind_context2)


def internal_bind_context3(
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
    See :class:`returns.primitives.interfaces.specific.reader.ReaderBased3`
    for more info.

    """
    return container.bind_context(function)


#: Kinded version of :func:`~internal_bind_context3`,
#: use it to infer real return type.
bind_context3 = kinded(internal_bind_context3)

#: Useful alias for :func:`~bind_context3`.
bind_context = bind_context3
