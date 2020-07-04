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
