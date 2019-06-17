# -*- coding: utf-8 -*-

from returns.maybe import Maybe
from returns.result import Failure, Success


def result_to_maybe(result_container):
    """Converts ``Result`` container to ``Maybe`` container."""
    return Maybe.new(result_container.value_or(None))


def maybe_to_result(maybe_container):
    """Converts ``Maybe`` container to ``Result`` container."""
    inner_value = maybe_container.value_or(None)
    if inner_value is not None:
        return Success(inner_value)
    return Failure(inner_value)
