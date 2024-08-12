
from typing import Iterable, List, TypeVar

from returns.interfaces.specific import  result
from returns.primitives.exceptions import UnwrapFailedError

_ValueType = TypeVar('_ValueType', covariant=True)
_ErrorType = TypeVar('_ErrorType', covariant=True)
_AdditionalType = TypeVar('_AdditionalType')


def partition(
    containers: Iterable[
        result.UnwrappableResult[_ValueType, _ErrorType, _AdditionalType, _ValueType, _ErrorType],
    ],
) -> tuple[List[_ValueType], List[_ErrorType]]:
    """
    Partition a list of results into successful and failed unwrapped values.

    Preserves order.

    .. code:: python

        >>> from returns.result import Failure, Success
        >>> from returns.methods import partition
        >>> results = [Success(1), Failure(2), Success(3), Failure(4)]
        >>> partition(results)
        ([1, 3], [2, 4])

    """
    successes = []
    failures = []
    for container in containers:
        try:
            successes.append(container.unwrap())
        except UnwrapFailedError:
            failures.append(container.failure())
    return successes, failures
