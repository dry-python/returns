# -*- coding: utf-8 -*-


def _flatten(container):
    """
    Joins two nested containers together.

    Please, note that it will not join
    two ``Failure`` for ``Result`` case
    or two ``Nothing`` for ``Maybe`` case together.

    .. code:: python

      >>> from returns.converters import flatten
      >>> from returns.maybe import Some
      >>> from returns.result import Failure, Success
      >>> from returns.io import IO, IOSuccess, IOFailure
      >>> from returns.context import Context

      >>> assert flatten(IO(IO(1))) == IO(1)

      >>> assert flatten(Some(Some(1))) == Some(1)

      >>> assert flatten(Success(Success(1))) == Success(1)
      >>> assert flatten(Failure(Failure(1))) == Failure(Failure(1))

      >>> assert flatten(IOSuccess(IOSuccess(1))) == IOSuccess(1)
      >>> assert flatten(IOFailure(IOFailure(1))) == IOFailure(IOFailure(1))

      >>> assert flatten(
      ...     Context.unit(Context.unit(1)),
      ... )(Context.Empty) == 1

    See also:
        https://bit.ly/2sIviUr

    """
    return container.bind(lambda identity: identity)  # we cannot import it :(
