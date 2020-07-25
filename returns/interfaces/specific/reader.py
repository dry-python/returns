"""
This module is special.

``Reader`` does not produce ``ReaderBasedN`` interface as other containers.

Because ``Reader`` can be used with two or three type arguments:
- ``RequiresContext[value, env]``
- ``RequiresContextResult[value, error, env]``

Because the second type argument changes its meaning
based on the used ``KindN`` instance,
we need to have two separate interfaces for two separate use-cases:
- ``ReaderBased2`` is used for types where the second type argument is ``env``
- ``ReaderBased3`` is used for types where the third type argument is ``env``

We also have two methods and two poinfree helpers
for ``bind_context`` composition: one for each interface.

Furthermore, ``Reader`` cannot have ``ReaderBased1`` type,
because we need both ``value`` and ``env`` types at all cases.

See also:
    https://github.com/dry-python/returns/issues/485

"""

from abc import abstractmethod, abstractproperty
from typing import TYPE_CHECKING, Any, Callable, NoReturn, Type, TypeVar

from returns.interfaces import applicative, bindable, mappable
from returns.primitives.hkt import Kind2, Kind3

if TYPE_CHECKING:
    from returns.context import RequiresContext, NoDeps  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_ReaderBased2Type = TypeVar('_ReaderBased2Type', bound='ReaderBased2')
_ReaderBased3Type = TypeVar('_ReaderBased3Type', bound='ReaderBased3')


class ReaderBased2(
    mappable.MappableN[_FirstType, _SecondType, NoReturn],
    bindable.BindableN[_FirstType, _SecondType, NoReturn],
    applicative.ApplicativeN[_FirstType, _SecondType, NoReturn],
):
    """
    Reader interface for ``Kind2`` based types.

    It has two type arguments and treats the second type argument as env type.
    """

    @abstractmethod
    def __call__(self, deps: _SecondType) -> _FirstType:
        """Calls the reader with the env to get the result back."""

    @abstractproperty
    def empty(self: _ReaderBased2Type) -> 'NoDeps':
        """Is required to call ``Reader`` with explicit empty argument."""

    @abstractmethod
    def bind_context(
        self: _ReaderBased2Type,
        function: Callable[
            [_FirstType],
            'RequiresContext[_UpdatedType, _SecondType]',
        ],
    ) -> Kind2[_ReaderBased2Type, _UpdatedType, _SecondType]:
        """Allows to apply a wrapped function over a ``Reader`` container."""

    @classmethod
    @abstractmethod
    def ask(
        cls: Type[_ReaderBased2Type],
    ) -> Kind2[_ReaderBased2Type, _SecondType, _SecondType]:
        """Returns the depedencies inside the container."""

    @classmethod
    @abstractmethod
    def from_context(
        cls: Type[_ReaderBased2Type],  # noqa: N805
        inner_value: 'RequiresContext[_FirstType, _SecondType]',
    ) -> Kind2[_ReaderBased2Type, _FirstType, _SecondType]:
        """Unit method to create new containers from successful ``Reader``."""


class ReaderBased3(
    mappable.MappableN[_FirstType, _SecondType, _ThirdType],
    bindable.BindableN[_FirstType, _SecondType, _ThirdType],
    applicative.ApplicativeN[_FirstType, _SecondType, _ThirdType],
):
    """
    Reader interface for ``Kind3`` based types.

    It has three type arguments and treats the third type argument as env type.
    The second type argument is not used here.
    """

    @abstractmethod
    def __call__(self, deps: _ThirdType) -> Any:
        """
        Calls the reader with the env to get the result back.

        Returns ``Any``, because we cannot know in advance
        what combitation of ``_FirstType`` and ``_SecondType`` would be used.
        It can be ``Union[_FirstType, _SecondType]`` or ``Tuple`` or ``Result``.
        Or any other type.
        """

    @abstractproperty
    def empty(self: _ReaderBased3Type) -> 'NoDeps':
        """Is required to call ``Reader`` with explicit empty argument."""

    @abstractmethod
    def bind_context(
        self: _ReaderBased3Type,
        function: Callable[
            [_FirstType],
            'RequiresContext[_UpdatedType, _ThirdType]',
        ],
    ) -> Kind3[_ReaderBased3Type, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to apply a wrapped function over a ``Reader`` container."""

    @classmethod
    @abstractmethod
    def ask(
        cls: Type[_ReaderBased3Type],
    ) -> Kind3[_ReaderBased3Type, _ThirdType, _SecondType, _ThirdType]:
        """Returns the depedencies inside the container."""

    @classmethod
    @abstractmethod
    def from_context(
        cls: Type[_ReaderBased3Type],  # noqa: N805
        inner_value: 'RequiresContext[_FirstType, _ThirdType]',
    ) -> Kind3[_ReaderBased3Type, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from successful ``Reader``."""
