from typing import Callable, Iterable, Sequence, Type, TypeVar

from returns._internal.iterable import internal_iterable_kind
from returns.interfaces.specific.result import ResultLikeN
from returns.primitives.hkt import Kinded, KindN, kinded
from returns.primitives.iterables import CollectAll

# Definitions:
_FirstType = TypeVar('_FirstType', contravariant=True)
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_ResultKind = TypeVar('_ResultKind', bound=ResultLikeN)


def validate(  # noqa: WPS234
    container_type: Type[_ResultKind],
    steps: Iterable[
        Callable[
            [_FirstType],
            KindN[_ResultKind, _FirstType, _SecondType, _ThirdType],
        ]
    ],
) -> Kinded[Callable[
    [_FirstType],
    KindN[_ResultKind, _FirstType, Sequence[_SecondType], _ThirdType],
]]:
    """
    Functional validation.

    Works with any ``ResultLikeN`` type.
    """

    @kinded
    def factory(instance: _FirstType) -> KindN[
        _ResultKind,
        _FirstType,
        Sequence[_SecondType],
        _ThirdType,
    ]:
        if not steps:
            return container_type.from_value(instance)

        swapped = [step(instance).swap() for step in steps]
        return internal_iterable_kind(
            container_type, swapped, CollectAll,
        ).bind(
            lambda errors: container_type.from_value(errors)
            if errors else container_type.from_failure(errors),
        ).swap()
    return factory
