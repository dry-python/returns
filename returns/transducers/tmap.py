from typing import Callable, TypeVar

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')

_AccValueType = TypeVar('_AccValueType')


def tmap(
    function: Callable[[_ValueType], _NewValueType],
) -> Callable[
    [Callable[[_AccValueType, _NewValueType], _AccValueType]],
    Callable[[_AccValueType, _ValueType], _AccValueType],
]:
    """
    A map implementation on a transducer form.

    .. code:: python

      >>> from typing import List
      >>> from returns.transducers import tmap, treduce

      >>> def add_one(number: int) -> int:
      ...     return number + 1

      >>> def append(collection: List[int], item: int) -> List[int]:
      ...     collection.append(item)
      ...     return collection

      >>> my_list = [0, 1]
      >>> xformaa = tmap(add_one)(append)
      >>> assert treduce(xformaa, my_list, []) == [1, 2]

    """
    def reducer(
        step: Callable[[_AccValueType, _NewValueType], _AccValueType],
    ) -> Callable[[_AccValueType, _ValueType], _AccValueType]:
        def map_(acc: _AccValueType, value: _ValueType) -> _AccValueType:
            return step(acc, function(value))
        return map_
    return reducer
