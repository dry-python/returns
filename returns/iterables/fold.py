from typing import Callable, Iterable, TypeVar, Sequence, Type, Tuple
from abc import abstractmethod
from typing_extensions import final

from returns.interfaces.applicative import ApplicativeN
from returns.interfaces.specific.result import ResultLikeN
from returns.primitives.hkt import KindN, kinded
from returns.maybe import Maybe, Some, Nothing

from typing_extensions import Protocol

# TODO: use it everywhere
@final
class _ConcatableSequence(  # type: ignore
    Protocol[_FirstType],
    Sequence[_FirstType],
):
    def __add__(
        self,
        other: Tuple[_FirstType, ...],
    ) -> '_ConcatableSequence[_FirstType]':
        ...


_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ApplicativeKind = TypeVar('_ApplicativeKind', bound=ApplicativeN)
_ResultKind = TypeVar('_ResultKind', bound=ResultLikeN)


class AbstractFold(object):
    """
    A collection of different helpers to write declarative ``Iterable`` actions.

    Allows to work with iterables.
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
        return cls._loop(iterable, default, function, concat_applicatives)

    @final
    @kinded
    @classmethod
    def collect(
        cls,
        iterable: Iterable[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[
            _ApplicativeKind,
            _ConcatableSequence[_FirstType],
            _SecondType,
            _ThirdType,
        ],
    ) -> KindN[
        _ApplicativeKind,
        _ConcatableSequence[_FirstType],
        _SecondType,
        _ThirdType,
    ]:
        return cls._collect(iterable, default)

    @final
    @kinded
    @classmethod
    def collect_all(
        cls,
        iterable: Iterable[
            KindN[_ResultKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[
            _ResultKind,
            _ConcatableSequence[_FirstType],
            _SecondType,
            _ThirdType,
        ],
    ) -> KindN[
        _ResultKind,
        _ConcatableSequence[_FirstType],
        _SecondType,
        _ThirdType,
    ]:
        return cls._collect_all(iterable, default)

    @classmethod
    @abstractmethod
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
        concat: Callable[[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
            KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
            KindN[
                _ApplicativeKind,
                Callable[[_UpdatedType], Callable[[_FirstType], _UpdatedType]],
                _SecondType,
                _ThirdType,
            ],
        ], KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]],
    ) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
        """
        Protected part of ``loop`` method.

        Can be replaced in subclasses for better performance, etc.
        """

    @classmethod
    def _collect(
        cls,
        iterable: Iterable[
            KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[
            _ApplicativeKind,
            _ConcatableSequence[_FirstType],
            _SecondType,
            _ThirdType,
        ],
    ) -> KindN[
        _ApplicativeKind,
        _ConcatableSequence[_FirstType],
        _SecondType,
        _ThirdType,
    ]:
        return cls._loop(
            iterable,
            default,
            _concat_sequence,
            concat_applicatives,
        )

    @classmethod
    def _collect_all(
        cls,
        iterable: Iterable[
            KindN[_ResultKind, _FirstType, _SecondType, _ThirdType],
        ],
        default: KindN[
            _ResultKind,
            _ConcatableSequence[_FirstType],
            _SecondType,
            _ThirdType,
        ],
    ) -> KindN[
        _ResultKind,
        _ConcatableSequence[_FirstType],
        _SecondType,
        _ThirdType,
    ]:
        return cls._loop(
            iterable,
            default,
            _concat_sequence,
            concat_applicatives_with_fallback,
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
        concat: Callable[
            [
                KindN[_ApplicativeKind, _FirstType, _SecondType, _ThirdType],
                KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
                KindN[
                    _ApplicativeKind,
                    Callable[
                        [_UpdatedType],
                        Callable[[_FirstType], _UpdatedType],
                    ],
                    _SecondType,
                    _ThirdType,
                ],
            ],
            KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType],
        ],
    ) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
        """
        Protected part of ``loop`` method.

        Can be replaced in subclasses for better performance, etc.
        """
        wrapped = default.from_value(function)
        for item in iterable:
            default = concat(item, default, wrapped)
        return default



def _concat_sequence(
    first: _ConcatableSequence[_FirstType],
) -> Callable[[_FirstType], _ConcatableSequence[_FirstType]]:
    return lambda second: first + (second, )


def concat_applicatives(
    current: KindN[
        _ApplicativeKind, _FirstType, _SecondType, _ThirdType,
    ],
    acc: KindN[
        _ApplicativeKind, _UpdatedType, _SecondType, _ThirdType,
    ],
    function: KindN[
        _ApplicativeKind,
        Callable[[_UpdatedType], Callable[[_FirstType], _UpdatedType]],
        _SecondType,
        _ThirdType,
    ],
) -> KindN[_ApplicativeKind, _UpdatedType, _SecondType, _ThirdType]:
    return current.apply(acc.apply(function))


def concat_applicatives_with_fallback(
    current: KindN[
        _ResultKind, _FirstType, _SecondType, _ThirdType,
    ],
    acc: KindN[
        _ResultKind, _UpdatedType, _SecondType, _ThirdType,
    ],
    function: KindN[
        _ResultKind,
        Callable[[_UpdatedType], Callable[[_FirstType], _UpdatedType]],
        _SecondType,
        _ThirdType,
    ],
) -> KindN[_ResultKind, _UpdatedType, _SecondType, _ThirdType]:
    return concat_applicatives(current, acc, function).rescue(lambda _: acc)


import anyio
from returns.result import Success, Failure
from returns.future import FutureSuccess, FutureFailure
from returns.io import IOSuccess
assert Fold.collect_all([Success(1), Failure(2)], Success(())) == Success((1,))

assert anyio.run(
    Fold.collect_all([FutureFailure(2), FutureSuccess(1)], FutureSuccess(())).awaitable,
) == IOSuccess((1,))
