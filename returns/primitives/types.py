# -*- coding: utf-8 -*-

from typing import Any, NoReturn

from returns.primitives.exceptions import ImmutableStateError


class Immutable(object):
    """Helper type for objects that should be immutable."""

    def __setattr__(self, attr_name: str, attr_value: Any) -> NoReturn:
        """Makes inner state of the containers immutable."""
        raise ImmutableStateError()

    def __delattr__(self, attr_name: str) -> NoReturn:  # noqa: WPS603
        """Makes inner state of the containers immutable."""
        raise ImmutableStateError()


class Stateless(object):
    """Helper type for object that should be empty."""

    __slots__ = ()
