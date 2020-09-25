from typing import TYPE_CHECKING, Callable, Iterable, TypeVar, Sequence
from abc import abstractmethod
from typing_extensions import final

from returns.interfaces.applicative import ApplicativeN
from returns.primitives.hkt import KindN, kinded
from returns.maybe import Maybe, Nothing


_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ApplicativeKind = TypeVar('_ApplicativeKind', bound=ApplicativeN)


class AbstractFold(object):
    """
    A collection of different helpers to write declarative ``Iterable`` actions.

    Allows to
    """

    @final
    @kinded
    @classmethod
    def loop(
        cls,
        iterable: Iterable[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
        function: Callable[
            [_UpdatedType],
            Callable[[_FirstType], _UpdatedType],
        ],
    ) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
        """
        Allows to make declarative loops.

        Looks like ``foldl`` in some other languages with some more specifics.
        See: https://philipschwarz.dev/fpilluminated/?page_id=348#bwg3/137

        Is also quite similar to ``reduce``.

        Public interface for ``loop`` method.
        Cannot be modified.
        """
        return cls._loop(iterable, default, function)

    @final
    @kinded
    @classmethod
    def loop_back(
        cls,
        iterable: Sequence[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
        function: Callable[
            [_FirstType],
            Callable[[_UpdatedType], _UpdatedType],
        ],
    ) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
        return cls._loop_back(iterable, default, function)

    @classmethod
    def any(
        cls,
        iterable: Iterable[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        predicate: Callable[[_FirstType], bool],
    ) -> bool:
        ...

    @classmethod
    def all(
        iterable: Iterable[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        predicate: Callable[[_FirstType], bool],
    ) -> bool:
        ...

    @abstractmethod
    @classmethod
    def _loop(
        cls,
        iterable: Iterable[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
        function: Callable[
            [_UpdatedType],
            Callable[[_FirstType], _UpdatedType],
        ],
    ) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
        """
        Protected part of ``loop`` method.

        Can be replaced in subclasses for better performance, etc.
        """

    @classmethod
    def _loop_back(
        cls,
        iterable: Sequence[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
        function: Callable[
            [_FirstType],
            Callable[[_UpdatedType], _UpdatedType],
        ],
    ) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
        return cls._loop(
            reversed(iterable),
            default,
            lambda x: lambda y: function(y)(x),
        )


class Fold(AbstractFold):
    """Concrete implementation of ``AbstractFold`` of end users."""

    @classmethod
    def _loop(
        cls,
        iterable: Iterable[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
        function: Callable[
            [_UpdatedType],
            Callable[[_FirstType], _UpdatedType],
        ],
    ) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
        """
        Protected part of ``loop`` method.

        Can be replaced in subclasses for better performance, etc.
        """
        wrapped = default.from_value(function)
        for item in iterable:
            default = item.apply(default.apply(wrapped))
        return default
