from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, ClassVar, Sequence, Type, TypeVar

from typing_extensions import final

from returns.interfaces.specific import reader, result
from returns.primitives.hkt import KindN
from returns.primitives.laws import (
    Law,
    Law2,
    Lawful,
    LawSpecDef,
    law_definition,
)

if TYPE_CHECKING:
    from returns.context import Reader, ReaderResult  # noqa: WPS433
    from returns.result import Result  # noqa: F401, WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_EnvType = TypeVar('_EnvType')

_ReaderResultLikeType = TypeVar(
    '_ReaderResultLikeType',
    bound='ReaderResultLikeN',
)


class ReaderResultLikeN(
    reader.ReaderLike3[_FirstType, _SecondType, _ThirdType],
    result.ResultLikeN[_FirstType, _SecondType, _ThirdType],
):
    """
    Base interface for all types that do look like ``ReaderResult`` instance.

    Cannot be called.
    """

    @abstractmethod
    def bind_context_result(
        self: _ReaderResultLikeType,
        function: Callable[
            [_FirstType],
            'ReaderResult[_UpdatedType, _SecondType, _ThirdType]',
        ],
    ) -> KindN[_ReaderResultLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Binds a ``ReaderResult`` returning function over a container."""

    @classmethod
    @abstractmethod
    def from_failed_context(
        cls: Type[_ReaderResultLikeType],  # noqa: N805
        inner_value: 'Reader[_ErrorType, _EnvType]',
    ) -> KindN[_ReaderResultLikeType, _FirstType, _ErrorType, _EnvType]:
        """Unit method to create new containers from failed ``Reader``."""

    @classmethod
    @abstractmethod
    def from_result_context(
        cls: Type[_ReaderResultLikeType],  # noqa: N805
        inner_value: 'ReaderResult[_ValueType, _ErrorType, _EnvType]',
    ) -> KindN[_ReaderResultLikeType, _ValueType, _ErrorType, _EnvType]:
        """Unit method to create new containers from ``ReaderResult``."""


#: Type alias for kinds with three type arguments.
ReaderResultLike3 = ReaderResultLikeN[_FirstType, _SecondType, _ThirdType]


@final
class _LawSpec(LawSpecDef):
    """
    Concrete laws for ``ReaderResulBasedN``.

    See: https://github.com/haskell/mtl/pull/61/files
    """

    @law_definition
    def purity_law(
        container: ReaderResultBasedN[_FirstType, _SecondType, _ThirdType],
        env: _ThirdType,
    ) -> None:
        """Calling a ``Reader`` twice has the same result with the same env."""
        assert container(env) == container(env)

    @law_definition
    def asking_law(
        container: ReaderResultBasedN[_FirstType, _SecondType, _ThirdType],
        env: _ThirdType,
    ) -> None:
        """Asking for an env, always returns the env."""
        assert container.ask().__call__(    # noqa: WPS609
            env,
        ) == container.from_value(env).__call__(env)  # noqa: WPS609


class ReaderResultBasedN(
    ReaderResultLikeN[_FirstType, _SecondType, _ThirdType],
    reader.CallableReader3[
        _FirstType,
        _SecondType,
        _ThirdType,
        # Calls:
        'Result[_FirstType, _SecondType]',
        _ThirdType,
    ],
    Lawful['ReaderResultBasedN[_FirstType, _SecondType, _ThirdType]'],
):
    """
    This interface is very specific to our ``ReaderResult`` type.

    The only thing that differs from ``ReaderResultLikeN`` is that we know
    the specific types for its ``__call__`` method.

    In this case the return type of ``__call__`` is ``Result``.
    """

    _laws: ClassVar[Sequence[Law]] = (
        Law2(_LawSpec.purity_law),
        Law2(_LawSpec.asking_law),
    )


#: Type alias for kinds with three type arguments.
ReaderResultBased3 = ReaderResultBasedN[_FirstType, _SecondType, _ThirdType]
