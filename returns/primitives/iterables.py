from abc import abstractmethod
from functools import reduce
from typing import TYPE_CHECKING, Callable, Generic, Iterable, Sequence, TypeVar

from returns.interfaces.rescuable import RescuableN
from returns.primitives.hkt import KindN

if TYPE_CHECKING:
    from returns.interfaces.container import ContainerN  # noqa: F401

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_ContainerKind = TypeVar('_ContainerKind', bound='ContainerN')

#: We use this value to filter out temporary values.
_sentinel = object()


class BaseIterableStrategyN(Generic[_FirstType, _SecondType, _ThirdType]):
    """
    Base class for creating strategies to work with iterables.

    Inherit from it to create your own strategies.
    """

    __slots__ = ('_iterable', '_initial_value')

    def __init__(
        self,
        iterable: Iterable[
            KindN[_ContainerKind, _FirstType, _SecondType, _ThirdType],
        ],
        initial_value: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
    ) -> None:
        """We need the iterable collection and the initial value to start."""
        self._iterable = iterable
        self._initial_value = initial_value

    def __call__(self) -> KindN[
        _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
    ]:
        """By default we use ``reduce`` to go through the given iterable."""
        return reduce(
            self._do_reduce,
            self._iterable,
            self._initial_value,
        )

    def _concat(
        self,
        inner: Sequence[_FirstType],
    ) -> Callable[[_FirstType], Sequence[_FirstType]]:
        """Helper to combine two sequences together."""
        # We actually use `Tuple` (not just `Sequence`) inside:
        # TODO: we can probably need to fix this type
        return lambda cur: (
            inner + (cur,) if cur is not _sentinel else inner  # type: ignore
        )

    @abstractmethod
    def _do_reduce(
        self,
        acc: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
        current: KindN[
            _ContainerKind, _FirstType, _SecondType, _ThirdType,
        ],
    ) -> KindN[_ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType]:
        """Logic for making this stratefy unique on each step."""


class FailFast(BaseIterableStrategyN[_FirstType, _SecondType, _ThirdType]):
    """
    Strategy to fail on any existing ``Failure`` like type.

    It is enough to have even a single ``Failure`` value in iterable
    for this type to convert the whole operation result to ``Failure``.
    Let's see how it works:

    .. code:: python

      >>> from returns.result import Result, Success, Failure
      >>> from returns.primitives.iterables import FailFast

      >>> empty = []
      >>> all_success = [Success(1), Success(2), Success(3)]
      >>> has_failure = [Success(1), Failure('a'), Success(3)]
      >>> all_failures = [Failure('a'), Failure('b')]

      >>> assert Result.from_iterable(empty, FailFast) == Success(())
      >>> assert Result.from_iterable(
      ...    all_success, FailFast,
      ... ) == Success((1, 2, 3))
      >>> assert Result.from_iterable(has_failure, FailFast) == Failure('a')
      >>> assert Result.from_iterable(all_failures, FailFast) == Failure('a')

    By the way, ``FailFast`` is a default strategy for all types:

    .. code:: python

      >>> assert Result.from_iterable(empty) == Success(())
      >>> assert Result.from_iterable(all_success) == Success((1, 2, 3))
      >>> assert Result.from_iterable(has_failure) == Failure('a')
      >>> assert Result.from_iterable(all_failures) == Failure('a')

    """

    def _do_reduce(
        self,
        acc: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
        current: KindN[
            _ContainerKind, _FirstType, _SecondType, _ThirdType,
        ],
    ) -> KindN[_ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType]:
        return acc.bind(lambda inner_acc: current.map(self._concat(inner_acc)))


class CollectAll(BaseIterableStrategyN[_FirstType, _SecondType, _ThirdType]):
    """
    Strategy to extract all ``Success`` like values even if there are failues.

    If there's at least one ``Success`` and any amount of ``Failure`` values,
    we will still return ``Success``.
    We can return ``Failure`` for this strategy only in a single case:
    when there are only failures in an iterable.

    Let's see how it works:

    .. code:: python

      >>> from returns.result import Result, Success, Failure
      >>> from returns.primitives.iterables import CollectAll

      >>> empty = []
      >>> all_success = [Success(1), Success(2), Success(3)]
      >>> has_failure = [Success(1), Failure('a'), Success(3)]
      >>> all_failures = [Failure('a'), Failure('b')]

      >>> assert Result.from_iterable(empty, CollectAll) == Success(())
      >>> assert Result.from_iterable(
      ...    all_success, CollectAll,
      ... ) == Success((1, 2, 3))
      >>> assert Result.from_iterable(
      ...    has_failure, CollectAll,
      ... ) == Success((1, 3))
      >>> assert Result.from_iterable(all_failures, CollectAll) == Success(())

    """

    def _do_reduce(
        self,
        acc: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
        current: KindN[
            _ContainerKind, _FirstType, _SecondType, _ThirdType,
        ],
    ) -> KindN[_ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType]:
        return acc.bind(self._try_concat(acc, current))

    def _try_concat(
        self,
        acc: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
        current: KindN[
            _ContainerKind, _FirstType, _SecondType, _ThirdType,
        ],
    ):
        def factory(inner: Sequence[_FirstType]) -> KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ]:
            local = current
            if isinstance(current, RescuableN):
                local = current.rescue(  # type: ignore
                    lambda _: current.from_value(_sentinel),  # type: ignore
                )
            return local.map(self._concat(inner))
        return factory
