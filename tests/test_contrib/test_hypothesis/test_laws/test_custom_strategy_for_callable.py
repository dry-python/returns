"""
Test that we can register a custom strategy for callables.

We use the strategy to generates `Maybe`s and `Result`s for
`Kind1[_F_Applicative, _SecondType]`.

Without the custom strategy, we would simply get instances of `_Wrapper`, even
though it is not an `Applicative`, because `_Wrapper` is a subtype of `KindN`
and `hypothesis` doesn't know about that `KindN` is just emulating HKTs.
"""

from abc import abstractmethod
from collections.abc import Callable, Sequence
from typing import (
    Any,
    ClassVar,
    Generic,
    TypeAlias,
    TypeVar,
    final,
    get_args,
    get_origin,
)

from hypothesis import strategies as st
from typing_extensions import Never

from returns.contrib.hypothesis.containers import strategy_from_container
from returns.contrib.hypothesis.laws import check_all_laws
from returns.contrib.hypothesis.type_resolver import StrategyFactory
from returns.interfaces.applicative import ApplicativeN
from returns.interfaces.specific.maybe import MaybeLike2
from returns.maybe import Maybe
from returns.primitives.asserts import assert_equal
from returns.primitives.container import BaseContainer
from returns.primitives.hkt import Kind1, KindN, SupportsKind1
from returns.primitives.laws import (
    Law,
    Law2,
    Lawful,
    LawSpecDef,
    law_definition,
)
from returns.result import Result

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_ValueType = TypeVar('_ValueType')
_F_Applicative = TypeVar('_F_Applicative', bound=ApplicativeN)


@final
class _LawSpec(LawSpecDef):
    """Contrived laws for `_SomeIdentityN`."""

    __slots__ = ()

    @law_definition
    def idempotence_law(
        some_identity: '_SomeIdentityN',
        make_container: Callable[[], Kind1[_F_Applicative, _SecondType]],
    ) -> None:
        """Applying twice should give the same value as applying once.

        NOTE: We use a `Callable` to generate the container so that we can
        override the strategy easily. Overriding the strategy directly for
        `KindN` is not currently possible.
        """
        container = make_container()
        assert_equal(
            some_identity.do_nothing(some_identity.do_nothing(container)),
            some_identity.do_nothing(container),
        )


class _SomeIdentityN(
    Lawful['_SomeIdentityN[_FirstType, _SecondType, _ThirdType]'],
    Generic[_FirstType, _SecondType, _ThirdType],
):
    """Dummy interface that does nothing to an `Applicative` container."""

    __slots__ = ()

    _laws: ClassVar[Sequence[Law]] = (Law2(_LawSpec.idempotence_law),)

    @abstractmethod  # noqa: WPS125
    def do_nothing(
        self,
        container: Kind1[_F_Applicative, _ValueType],
    ) -> Kind1[_F_Applicative, _ValueType]:
        """No-op method that returns the container."""


_SomeIdentity1: TypeAlias = _SomeIdentityN[_FirstType, Never, Never]


class _Wrapper(
    BaseContainer,
    SupportsKind1['_Wrapper', _FirstType],
    _SomeIdentity1[_FirstType],
):
    """Simple instance of `_SomeIdentityN`."""

    _inner_value: _FirstType

    def __init__(self, inner_value: _FirstType) -> None:
        super().__init__(inner_value)

    def do_nothing(
        self,
        container: Kind1[_F_Applicative, _ValueType],
    ) -> Kind1[_F_Applicative, _ValueType]:
        """No-op method that returns the container."""
        return container


def _callable_strategy(
    arg1: type[object], arg2: type[object]
) -> StrategyFactory[Callable]:
    type_arg1 = int if arg1 == Any else arg1  # type: ignore[comparison-overlap]
    type_arg2 = int if arg2 == Any else arg2  # type: ignore[comparison-overlap]
    return_results = st.functions(
        pure=True,
        returns=strategy_from_container(Result)(Result[type_arg1, type_arg2]),  # type: ignore[valid-type]
    )
    return_maybes = st.functions(
        pure=True,
        returns=strategy_from_container(Maybe)(
            MaybeLike2[type_arg1, type_arg2]  # type: ignore[valid-type]
        ),
    )
    return st.one_of(return_results, return_maybes)


def _callable_factory(thing: type[object]) -> StrategyFactory[Callable]:
    if get_origin(thing) != Callable:
        raise NotImplementedError

    match get_args(thing):
        case [[], return_type] if (
            get_origin(return_type) == KindN
            and get_args(return_type)[0] == _F_Applicative
        ):
            type1, type2, *_ = get_args(return_type)[1:]
            return _callable_strategy(type1, type2)
        case _:
            raise NotImplementedError


other_strategies: dict[type[object], StrategyFactory] = {
    Callable: _callable_factory  # type: ignore[dict-item]
}

check_all_laws(
    _Wrapper,
    container_strategy=st.builds(_Wrapper, st.integers()),
    other_strategies=other_strategies,
)
