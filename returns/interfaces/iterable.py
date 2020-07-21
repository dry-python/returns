from abc import abstractmethod
from typing import Generic, Iterable, NoReturn, Sequence, Type, TypeVar

from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_IterableType = TypeVar('_IterableType', bound='IterableN')


class IterableN(Generic[_FirstType, _SecondType, _ThirdType]):
    """
    Allows to work with iterables of containers.

    Coverts ``Iterable[Container[...]]`` to ``Container[Sequence[...]]``
    """

    @classmethod
    @abstractmethod
    def from_iterable(
        cls: Type[_IterableType],  # noqa: N805
        inner_value: Iterable[
            KindN[_IterableType, _FirstType, _SecondType, _ThirdType],
        ],
    ) -> KindN[_IterableType, Sequence[_FirstType], _SecondType, _ThirdType]:
        """Unit method to create a new container from iterable of containers."""


#: Type alias for kinds with one type argument.
Iterable1 = IterableN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Iterable2 = IterableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Iterable3 = IterableN[_FirstType, _SecondType, _ThirdType]
