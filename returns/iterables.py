from abc import abstractmethod
from functools import reduce
from typing import Callable, Generic, Iterable, Optional, Sequence, TypeVar

from returns.interfaces.aliases.container import ContainerN
from returns.interfaces.rescuable import RescuableN
from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_ContainerKind = TypeVar('_ContainerKind', bound=ContainerN)


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
        inner_acc: Sequence[_FirstType],
    ) -> Callable[[_FirstType], Sequence[_FirstType]]:
        """Helper to combine two sequences together."""
        # We actually use `Tuple` (not `Sequence`) inside:
        # TODO: we can probably need to fix this type
        return lambda current: inner_acc + (current,)  # type: ignore

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
      >>> from returns.iterables import FailFast

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
      >>> from returns.iterables import CollectAll

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
      >>> assert Result.from_iterable(all_failures, CollectAll) == Failure('b')

    One more interesting thing about this class is that
    it is using side-effects together with functional composition
    to make the logic way easier. Side-effects are locked into this class,
    there's no way they can harm other pieces of code.

    """

    __slots__ = ('_at_least_one', '_last_failure')

    def __init__(
        self,
        iterable: Iterable[
            KindN[_ContainerKind, _FirstType, _SecondType, _ThirdType],
        ],
        initial_value: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
    ) -> None:
        """We also track that we have at least one value and a last failure."""
        super().__init__(iterable, initial_value)
        self._at_least_one: bool = False
        self._last_failure: Optional[KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ]] = None

    def __call__(self) -> KindN[
        _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
    ]:
        """We need to override the base method to add post-processing."""
        parent_value: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ] = super().__call__()
        if self._last_failure and not self._at_least_one:
            return self._last_failure
        return parent_value

    def _do_reduce(
        self,
        acc: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
        current: KindN[
            _ContainerKind, _FirstType, _SecondType, _ThirdType,
        ],
    ) -> KindN[_ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType]:
        new_acc = acc.bind(
            lambda inner_acc: current.map(self._concat(inner_acc)),
        ).map(self._mark_success)
        if isinstance(new_acc, RescuableN):
            # This is a hack we use for ignroing failues, if any:
            return new_acc.rescue(  # type: ignore
                lambda _: self._save_last_failure(new_acc),  # type: ignore
            ).rescue(lambda _: acc)  # type: ignore
        return new_acc

    def _save_last_failure(
        self,
        failed: KindN[
            _ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType,
        ],
    ) -> KindN[_ContainerKind, Sequence[_FirstType], _SecondType, _ThirdType]:
        self._last_failure = failed  # this is actually a side effect
        return failed

    def _mark_success(
        self, inner_value: Sequence[_FirstType],
    ) -> Sequence[_FirstType]:
        self._at_least_one = True  # this is actually a side effect
        return inner_value
