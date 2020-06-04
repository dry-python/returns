from typing_extensions import final

from returns.context import RequiresContextFutureResult, RequiresContextIOResult
from returns.future import FutureResult
from returns.io import IOResult
from returns.primitives.types import Immutable


@final
class _managed(Immutable):  # noqa: N801
    """
    Allows to run managed computation.

    Managed computations consist of three steps:

    1. ``acquire`` when we get some initial resource to work with
    2. ``use`` when the main logic is done
    3. ``release`` when we release acquired resource

    Let's look at the example:

    1. We need to acquire an opened file to read it later
    2. We need to use acquired file to read its content
    3. We need to release the acquired file in the end

    Here's a code example:

    .. code:: python

      >>> from returns.pipeline import managed
      >>> from returns.io import IOSuccess, IOFailure, impure_safe

      >>> class Lock(object):
      ...     '''Example class to emulate state to acquire and release.'''
      ...     def __init__(self, default: bool = False) -> None:
      ...         self.set = default
      ...     def __eq__(self, lock) -> bool:  # we need this for testing
      ...         return self.set == lock.set
      ...     def release(self) -> None:
      ...         self.set = False

      >>> pipeline = managed(
      ...     lambda lock: IOSuccess(lock) if lock.set else IOFailure(False),
      ...     lambda lock, use_result: impure_safe(lock.release)(),
      ... )

      >>> assert pipeline(IOSuccess(Lock(True))) == IOSuccess(Lock(False))
      >>> assert pipeline(IOSuccess(Lock())) == IOFailure(False)
      >>> assert pipeline(IOFailure('no lock')) == IOFailure('no lock')

    See also:
        - https://github.com/gcanti/fp-ts/blob/master/src/IOEither.ts
        - https://zio.dev/docs/datatypes/datatypes_managed

    Implementation
    ~~~~~~~~~~~~~~
    This class requires some explanation.

    First of all, we modeled this function as a class,
    so it can be partially applied easily.

    Secondly, we used imperative approach of programming inside this class.
    Functional approached was 2 times slower.
    And way more complex to read and understand.

    Lastly, we try to hide these two things for the end user.
    We pretend that this is not a class, but a function.
    We also do not break a functional abstraction for the end user.
    It is just an implementation detail.

    Type inference does not work so well with ``lambda`` functions.
    But, we do not recommend to use this function with ``lambda`` functions.

    """

    __slots__ = ('_use', '_release')

    def __init__(self, use, release):
        """Saving the ``use`` and ``release`` steps."""
        object.__setattr__(self, '_use', use)  # noqa: WPS609
        object.__setattr__(self, '_release', release)  # noqa: WPS609

    def __call__(self, acquire):
        """
        Calling the pipeline by providing the first ``acquire`` step.

        It might look like a typeclass,
        but typeclass support is not yet enabled in our project.
        So, it is just a bunch of ``if`` statements for now.
        """
        if isinstance(acquire, IOResult):
            return acquire.bind(self._ioresult_pipeline)
        elif isinstance(acquire, RequiresContextIOResult):
            return acquire.bind(self._reader_ioresult_pipeline)
        elif isinstance(acquire, RequiresContextFutureResult):
            return acquire.bind(self._reader_future_result_pipeline)
        return acquire.bind_async(self._future_pipeline)

    def _ioresult_pipeline(self, inner_value):
        used = self._use(inner_value)
        inner_result = used._inner_value  # noqa: WPS437
        self._release(inner_value, inner_result)
        return used

    def _reader_ioresult_pipeline(self, inner_value):
        def factory(deps):
            return _managed(
                lambda inner: self._use(inner)(deps),
                lambda inner, pure: self._release(inner, pure)(deps),
            )(IOResult.from_value(inner_value))
        return RequiresContextIOResult(factory)

    async def _future_pipeline(self, inner_value):
        used = self._use(inner_value)
        inner_result = await used._inner_value  # noqa: WPS437
        await self._release(inner_value, inner_result)
        return FutureResult.from_result(inner_result)

    def _reader_future_result_pipeline(self, inner_value):
        def factory(deps):
            return _managed(
                lambda inner: self._use(inner)(deps),
                lambda inner, pure: self._release(inner, pure)(deps),
            )(FutureResult.from_value(inner_value))
        return RequiresContextFutureResult(factory)
