"""
This module is special.

``Reader`` does not produce ``ReaderLikeN`` interface as other containers.

Because ``Reader`` can be used with two or three type arguments:
- ``RequiresContext[value, env]``
- ``RequiresContextResult[value, error, env]``

Because the second type argument changes its meaning
based on the used ``KindN`` instance,
we need to have two separate interfaces for two separate use-cases:
- ``ReaderLike2`` is used for types where the second type argument is ``env``
- ``ReaderLike3`` is used for types where the third type argument is ``env``

We also have two methods and two poinfree helpers
for ``bind_context`` composition: one for each interface.

Furthermore, ``Reader`` cannot have ``ReaderLike1`` type,
because we need both ``value`` and ``env`` types at all cases.

See also:
    https://github.com/dry-python/returns/issues/485

"""

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generic, Type, TypeVar

from returns.interfaces import container
from returns.primitives.hkt import Kind2, Kind3

if TYPE_CHECKING:
    from returns.context import RequiresContext, NoDeps  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')
_EnvType = TypeVar('_EnvType')

_ReaderLike2Type = TypeVar('_ReaderLike2Type', bound='ReaderLike2')
_ReaderLike3Type = TypeVar('_ReaderLike3Type', bound='ReaderLike3')


class CanBeCalled(Generic[_ValueType, _EnvType]):
    @abstractmethod
    def __call__(self, deps: _EnvType) -> _ValueType:
        ...


class ReaderLike2(
    container.Container2[_FirstType, _SecondType],
):
    """
    Reader interface for ``Kind2`` based types.

    It has two type arguments and treats the second type argument as env type.
    """

    @property
    @abstractmethod
    def empty(self: _ReaderLike2Type) -> 'NoDeps':
        """Is required to call ``Reader`` with explicit empty argument."""

    @abstractmethod
    def bind_context(
        self: _ReaderLike2Type,
        function: Callable[
            [_FirstType],
            'RequiresContext[_UpdatedType, _SecondType]',
        ],
    ) -> Kind2[_ReaderLike2Type, _UpdatedType, _SecondType]:
        """Allows to apply a wrapped function over a ``Reader`` container."""

    @abstractmethod
    def modify_env(
        self: _ReaderLike2Type,
        function: Callable[[_UpdatedType], _SecondType],
    ) -> Kind2[_ReaderLike2Type, _FirstType, _UpdatedType]:
        """Transforms the environment before calling the container."""

    @classmethod
    @abstractmethod
    def ask(
        cls: Type[_ReaderLike2Type],
    ) -> Kind2[_ReaderLike2Type, _SecondType, _SecondType]:
        """Returns the depedencies inside the container."""

    @classmethod
    @abstractmethod
    def from_context(
        cls: Type[_ReaderLike2Type],  # noqa: N805
        inner_value: 'RequiresContext[_ValueType, _EnvType]',
    ) -> Kind2[_ReaderLike2Type, _ValueType, _EnvType]:
        """Unit method to create new containers from successful ``Reader``."""


class ReaderLike3(
    container.Container3[_FirstType, _SecondType, _ThirdType],
):
    """
    Reader interface for ``Kind3`` based types.

    It has three type arguments and treats the third type argument as env type.
    The second type argument is not used here.
    """

    @property
    @abstractmethod
    def empty(self: _ReaderLike3Type) -> 'NoDeps':
        """Is required to call ``Reader`` with explicit empty argument."""

    @abstractmethod
    def bind_context(
        self: _ReaderLike3Type,
        function: Callable[
            [_FirstType],
            'RequiresContext[_UpdatedType, _ThirdType]',
        ],
    ) -> Kind3[_ReaderLike3Type, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to apply a wrapped function over a ``Reader`` container."""

    @abstractmethod
    def modify_env(
        self: _ReaderLike3Type,
        function: Callable[[_UpdatedType], _ThirdType],
    ) -> Kind3[_ReaderLike3Type, _FirstType, _SecondType, _UpdatedType]:
        """Transforms the environment before calling the container."""

    @classmethod
    @abstractmethod
    def ask(
        cls: Type[_ReaderLike3Type],
    ) -> Kind3[_ReaderLike3Type, _ThirdType, _SecondType, _ThirdType]:
        """Returns the depedencies inside the container."""

    @classmethod
    @abstractmethod
    def from_context(
        cls: Type[_ReaderLike3Type],  # noqa: N805
        inner_value: 'RequiresContext[_ValueType, _EnvType]',
    ) -> Kind3[_ReaderLike3Type, _ValueType, _SecondType, _EnvType]:
        """Unit method to create new containers from successful ``Reader``."""


class CallableReader2(
    ReaderLike2[_FirstType, _SecondType],
    CanBeCalled[_ValueType, _EnvType],
):
    ...


class ReaderBased2(
    CallableReader2[
        _FirstType,
        _SecondType,
        # Used for call typing:
        _FirstType,
        _SecondType,
    ],
):
    ...
