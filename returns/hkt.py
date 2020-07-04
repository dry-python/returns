from typing import Generic, TypeVar

_InstanceType = TypeVar('_InstanceType')
_TypeArgTypes = TypeVar('_TypeArgTypes')


class Kind(Generic[_InstanceType, _TypeArgTypes]):
    """
    Emulation support for Higher Kinded Types.

    We use a custom ``mypy`` plugin to make sure types are correct.
    Otherwise, it is currently impossible to properly type this.

    We use "emulated Higher Kinded Types" concept.

    See also:
        https://arrow-kt.io/docs/0.10/patterns/glossary/#higher-kinds
        https://github.com/gcanti/fp-ts/blob/master/docs/guides/HKT.md
        https://bow-swift.io/docs/fp-concepts/higher-kinded-types

    """

    __slots__ = ()

    def __class_getitem__(cls, type_params):  # noqa: N805
        """Used to suppress generic validation."""
        if not isinstance(type_params, tuple):
            type_params = (type_params,)  # noqa: WPS434

        real_args = len(cls.__parameters__)  # type: ignore
        return super().__class_getitem__(  # type: ignore
            type_params[:real_args],
        )
