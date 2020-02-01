# -*- coding: utf-8 -*-

from returns.context import RequiresContext
from returns.io import IO


def _squash_io(*args):
    """
    Unwraps ``IO`` values, merges them into tuple, and wraps back.

    .. code:: python

        >>> from returns.io import IO
        >>> from returns.converters import squash_io
        >>> assert squash_io(IO('a'), IO('b')) == IO(('a', 'b'))

    Why this only exists for ``IO`` and ``RequiresContext``?
    Because these types represent real values, that do not possibly fail.

    How would you, for example, squash two ``Result`` values?
    ``Success(1)`` and ``Failure(2)`` would not give you a tuple when squashed.
    """
    return IO(tuple(
        container._inner_value  # noqa:  WPS437
        for container in args
    ))


def _squash_context(*args):
    """
    Unwraps ``RequiresContext`` values, merges them into tuple, and wraps back.

    .. code:: python

        >>> from returns.context import RequiresContext
        >>> from returns.converters import squash_context
        >>> assert squash_context(
        ...     RequiresContext.from_value(1),
        ...     RequiresContext.from_value('a'),
        ...     RequiresContext.from_value(True),
        ... )(...) == RequiresContext.from_value((1, 'a', True))(...)

    See :func:`returns.converters.squash_io` for more docs.
    """
    return RequiresContext(lambda deps: tuple(
        func(deps)
        for func in args
    ))
