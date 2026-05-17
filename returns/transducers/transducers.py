from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Optional,
    TypeVar,
    final,
    overload,
)

from returns.primitives.types import Immutable

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')

_AccValueType = TypeVar('_AccValueType')


@final
class Reduced(Immutable, Generic[_ValueType]):
    """
    Sentinel for early termination inside transducer.

    .. code:: python

      >>> from returns.transducers import tmap, transduce, Reduced

      >>> def add_one(number: int) -> int:
      ...     return number + 1

      >>> def add(acc: int, number: int) -> int:
      ...     if acc == 3:
      ...         return Reduced(acc)
      ...     return acc + number

      >>> my_list = [0, 1, 2]
      >>> assert transduce(tmap(add_one), add, 0, my_list) == 3

    """

    __slots__ = ('_inner_value',)

    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        """Encapsulates the value from early reduce termination."""
        object.__setattr__(self, '_inner_value', inner_value)  # noqa: WPS609

    @property
    def value(self) -> _ValueType:  # noqa: WPS110
        """Returns the value from early reduce termination."""
        return self._inner_value


@final
class _Missing(Immutable):
    """Represents a missing value for reducers."""

    __slots__ = ('_instance',)

    _instance: Optional['_Missing'] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> '_Missing':
        if cls._instance is None:
            cls._instance = object.__new__(cls)  # noqa: WPS609
        return cls._instance


#: A singleton representing any missing value
Missing = _Missing()


def transduce(
    xform: Callable[
        [Callable[[_AccValueType, _ValueType], _AccValueType]],
        Callable[[_AccValueType, _ValueType], _AccValueType],
    ],
    reducing_function: Callable[[_AccValueType, _ValueType], _AccValueType],
    initial: _AccValueType,
    iterable: Iterable[_ValueType],
) -> _AccValueType:
    """
    Process information with transducers.

    .. code:: python

      >>> from returns.transducers import tmap, transduce

      >>> def add_one(number: int) -> int:
      ...     return number + 1

      >>> def add(acc: int, number: int) -> int:
      ...     return acc + number

      >>> my_list = [0, 1, 2]
      >>> assert transduce(tmap(add_one), add, 0, my_list) == 6
    """
    reducer = xform(reducing_function)
    return treduce(reducer, iterable, initial)


@overload
def treduce(
    function: Callable[[_ValueType, _ValueType], _ValueType],
    iterable: Iterable[_ValueType],
    initial: _Missing = Missing,
) -> _ValueType:
    """Reduce without an initial value."""


@overload
def treduce(
    function: Callable[[_AccValueType, _ValueType], _AccValueType],
    iterable: Iterable[_ValueType],
    initial: _AccValueType,
) -> _AccValueType:
    """Reduce with an initial value."""


def treduce(function, iterable, initial=Missing):
    """
    A rewritten version of :func:`reduce <functools.reduce>`.

    This version considers some features borrowed from Clojure:

    - Early termination
    - Function initializer [TODO]

    You can use it as a normal reduce if you want:

    .. code:: python

      >>> from returns.transducers import treduce

      >>> def add(acc: int, value: int) -> int:
      ...     return acc + value

      >>> assert treduce(add, [1, 2, 3]) == 6

    """
    it = iter(iterable)

    if initial is Missing:
        try:
            acc_value = next(it)
        except StopIteration:
            raise TypeError(
                'reduce() of empty iterable with no initial value',
            ) from None
    else:
        acc_value = initial

    for value in it:  # noqa: WPS110
        acc_value = function(acc_value, value)
        if isinstance(acc_value, Reduced):
            return acc_value.value
    return acc_value
