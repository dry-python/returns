from typing import Callable, TypeVar

_ValueType = TypeVar('_ValueType')
_AccValueType = TypeVar('_AccValueType')


def tfilter(
    predicate: Callable[[_ValueType], bool],
) -> Callable[
    [Callable[[_AccValueType, _ValueType], _AccValueType]],
    Callable[[_AccValueType, _ValueType], _AccValueType],
]:
    """
    :py:func:`filter <filter>` implementation on a transducer form.

    .. code:: python

      >>> from typing import List
      >>> from returns.transducers import tfilter, treduce

      >>> def is_even(number: int) -> bool:
      ...     return number % 2 == 0

      >>> def append(collection: List[int], item: int) -> List[int]:
      ...     collection.append(item)
      ...     return collection

      >>> my_list = [0, 1, 2, 3, 4, 5, 6]
      >>> xform = tfilter(is_even)(append)
      >>> assert treduce(xform, my_list, []) == [0, 2, 4, 6]

    """
    def reducer(
        step: Callable[[_AccValueType, _ValueType], _AccValueType],
    ) -> Callable[[_AccValueType, _ValueType], _AccValueType]:
        def filter_(acc: _AccValueType, value: _ValueType) -> _AccValueType:
            if predicate(value):
                return step(acc, value)
            return acc
        return filter_
    return reducer
