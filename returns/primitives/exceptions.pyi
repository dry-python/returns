# -*- coding: utf-8 -*-

from typing import TypeVar

from returns.primitives.container import Container

_ContainerType = TypeVar('_ContainerType', bound=Container)


class UnwrapFailedError(Exception):
    def __init__(self, container: _ContainerType) -> None:
        self.halted_container = container


class ImmutableStateError(Exception):
    ...
