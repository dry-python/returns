# -*- coding: utf-8 -*-

from typing import TypeVar

from returns.io import IO

_ValueType = TypeVar('_ValueType')


def unsafe_perform_io(wrapped_in_io: IO[_ValueType]) -> _ValueType:
    """
    Compatibility utility and escape mechanism from ``IO`` world.

    Just unwraps the internal value
    from :class:`returns.io.IO` container.
    Should be used with caution!
    Since it might be overused by lazy and ignorant developers.

    It is recommended to have only one place (module / file)
    in your program where you allow unsafe operations.

    We recommend to use ``import-linter`` to enforce this rule:

    - https://github.com/seddonym/import-linter

    .. code:: python

      >>> from returns.io import IO
      >>> unsafe_perform_io(IO(1))
      1

    """
    return wrapped_in_io._inner_value  # noqa: WPS437
