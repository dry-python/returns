from functools import reduce
from typing import Iterable, Sequence, TypeVar

from returns.interfaces.iterable import IterableN
from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_IterableKind = TypeVar('_IterableKind', bound=IterableN)


def _reducer(acc, current):
    return acc.bind(
        lambda inner_acc: current.map(
            lambda inner_current: inner_acc + (inner_current,),  # noqa: WPS430
        ),
    )


def iterable_kind(
    cls,  # TODO: type as `Union[_ApplicativeKind, _IterableKind]` after #474
    sequence: Iterable[
        KindN[_IterableKind, _FirstType, _SecondType, _ThirdType],
    ],
) -> KindN[_IterableKind, Sequence[_FirstType], _SecondType, _ThirdType]:
    """
    Evaluate container actions from iterable, collecting results.

    This function should not be used directly.
    Use ``.from_iterable`` container methods instead.

    It is a helper function for :class:`returns.interfaces.iterable.Iterable`.
    """
    return reduce(_reducer, sequence, cls.from_value(()))
