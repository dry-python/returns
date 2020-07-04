"""
Custom mypy plugin to solve the temporary problem with python typing.

Important: we don't do anything ugly here.
We only solve problems of the current typing implementation.

``mypy`` API docs are here:
https://mypy.readthedocs.io/en/latest/extending_mypy.html

We use ``pytest-mypy-plugins`` to test that it works correctly, see:
https://github.com/mkurnikov/pytest-mypy-plugins
"""
from typing import Callable, ClassVar, Mapping, Optional, Type

from mypy.plugin import (
    AnalyzeTypeContext,
    FunctionContext,
    MethodContext,
    MethodSigContext,
    Plugin,
)
from mypy.types import CallableType
from mypy.types import Type as MypyType
from typing_extensions import Final, final

from returns.contrib.mypy._features import (
    curry,
    decorators,
    flow,
    kind,
    partial,
    pipe,
    pointfree,
)

# Constant fullnames for typechecking
# ===================================

#: Set of full names of our decorators.
_TYPED_DECORATORS: Final = frozenset((
    'returns.result.safe',
    'returns.io.impure',
    'returns.io.impure_safe',
    'returns.maybe.maybe',
    'returns.future.future',
    'returns.future.asyncify',
    'returns.future.future_safe',
    'returns.functions.not_',
))

#: Used for cases when we return a protocol overloaded based on a return type.
_TYPED_PROTOCOL_OVERLOADED: Final = frozenset((
    # Pointfree functions:
    'returns._generated.pointfree.map._map',
    'returns._generated.pointfree.alt._alt',
    'returns._generated.pointfree.fix._fix',

    'returns._generated.pointfree.bind_result._bind_result',
    'returns._generated.pointfree.bind_io._bind_io',
    'returns._generated.pointfree.bind_ioresult._bind_ioresult',
    'returns._generated.pointfree.bind_future._bind_future',
    'returns._generated.pointfree.bind_async_future._bind_async_future',
    'returns._generated.pointfree.bind_future_result._bind_future_result',
    (
        'returns._generated.pointfree.bind_async_future_result.' +
        '_bind_async_future_result'
    ),
    'returns._generated.pointfree.bind_context._bind_context',
    'returns._generated.pointfree.bind_context_result._bind_context_result',
    'returns._generated.pointfree.bind_context_ioresult._bind_context_ioresult',
    'returns._generated.pointfree.bind_awaitable._bind_awaitable',

    'returns._generated.pointfree.value_or._value_or',
))

#: Used for typed ``partial`` function.
_TYPED_PARTIAL_FUNCTION: Final = 'returns.curry.partial'

#: Used for typed ``curry`` decorator.
_TYPED_CURRY_FUNCTION: Final = 'returns.curry.curry'

#: Used for typed ``flow`` call.
_TYPED_FLOW_FUNCTION: Final = 'returns._generated.pipeline.flow._flow'

#: Used for typed ``pipe`` call.
_TYPED_PIPE_FUNCTION: Final = 'returns._generated.pipeline.pipe._pipe'
_TYPED_PIPE_METHOD: Final = 'returns._generated.pipeline.pipe._Pipe.__call__'

#: Used for HKT emulation.
_TYPED_KIND: Final = 'returns.hkt.Kind'


# Type aliases
# ============

#: Types for a type analyze hook.
_AnalyzeCallback = Callable[[AnalyzeTypeContext], MypyType]
_AnalyzePlugin = Callable[[Plugin, str], _AnalyzeCallback]

#: Type for a function hook.
_FunctionCallback = Callable[[FunctionContext], MypyType]

#: Type for a method hook.
_MethodCallback = Callable[[MethodContext], MypyType]

#: Type for a method signature hook.
_MethodSigCallback = Callable[[MethodSigContext], CallableType]


# Interface
# =========

@final
class _ReturnsPlugin(Plugin):
    """Our main plugin to dispatch different callbacks to specific features."""

    _analyze_hook_plugins: ClassVar[Mapping[str, _AnalyzePlugin]] = {
        _TYPED_KIND: kind.analyze,
    }

    _function_hook_plugins: ClassVar[Mapping[str, _FunctionCallback]] = {
        _TYPED_PARTIAL_FUNCTION: partial.analyze,
        _TYPED_CURRY_FUNCTION: curry.analyze,
        _TYPED_FLOW_FUNCTION: flow.analyze,
        _TYPED_PIPE_FUNCTION: pipe.analyze,
        **dict.fromkeys(_TYPED_PROTOCOL_OVERLOADED, pointfree.analyze),
        **dict.fromkeys(_TYPED_DECORATORS, decorators.analyze),
    }

    _method_hook_plugins: ClassVar[Mapping[str, _MethodCallback]] = {
        _TYPED_PIPE_METHOD: pipe.infer,
    }

    _method_sig_hook_plugins: ClassVar[Mapping[str, _MethodSigCallback]] = {
        _TYPED_PIPE_METHOD: pipe.signature,
    }

    def get_type_analyze_hook(
        self,
        fullname: str,
    ) -> Optional[_AnalyzeCallback]:
        """
        Called for all types.

        Is called during semantic analizing phase.
        It does not have an access to a typechecker.
        It is used to transform types into different other types.
        """
        plugin = self._analyze_hook_plugins.get(fullname)
        if plugin is not None:
            return plugin(self, fullname)
        return None

    def get_function_hook(
        self,
        fullname: str,
    ) -> Optional[_FunctionCallback]:
        """
        Called for function return types from ``mypy``.

        Runs on each function call in the source code.
        We are only interested in a particular subset of all functions.
        So, we return a function handler for them.

        Otherwise, we return ``None``.
        """
        return self._function_hook_plugins.get(fullname)

    def get_method_hook(
        self,
        fullname: str,
    ) -> Optional[_MethodCallback]:
        """Called for method return types from ``mypy``."""
        return self._method_hook_plugins.get(fullname)

    def get_method_signature_hook(
        self,
        fullname: str,
    ) -> Optional[_MethodSigCallback]:
        """Called for method signature from ``mypy``."""
        return self._method_sig_hook_plugins.get(fullname)


def plugin(version: str) -> Type[Plugin]:
    """Plugin's public API and entrypoint."""
    return _ReturnsPlugin
