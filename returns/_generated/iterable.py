
from typing import Iterable, Sequence, Type, TypeVar

from returns.interfaces.aliases.container import ContainerN
from returns.iterables import BaseIterableStrategyN
from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_ContainerKind = TypeVar('_ContainerKind', bound=ContainerN)



def iterable_kind(
    cls,
    sequence: Iterable[
        KindN[_ContainerKind, _FirstType, _SecondType, _ThirdType],
    ],
    strategy: Type[
        BaseIterableStrategyN[_FirstType, _SecondType, _ThirdType],
    ],
) -> KindN[_ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType]:
    """
    Evaluate container actions from iterable, collecting results.

    This function should not be used directly.
    Use ``.from_iterable`` container methods instead.

    It is a helper function for :class:`returns.interfaces.iterable.Iterable`.

    See ``returns.iterables`` module for a list of supported strategies.

    Note: ``cls`` is not typed because of how ``mypy`` resolves the types.
    For some reason, there are a lot of problems with it.
    And since this is an internal function, we don't really care.
    """
    return strategy(sequence, cls.from_value(()))()
