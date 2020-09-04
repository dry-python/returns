# Version history

We follow Semantic Versions since the `1.0.0` release.
Versions before `1.0.0` are `0Ver`-based:
incremental in minor, bugfixes only are patches.
See [0Ver](https://0ver.org/).


## 0.15.0 WIP aka The initial HKT release

### Features

- Adds Higher Kinded Types partial support

- **Breaking**: makes our `mypy` plugin not optional, but required!
- **Breaking**: changes all `RequiresContext`-based type arguments order,
  previously we used to specify `_EnvType` as the first type argument,
  now it is the last one. This is done to respect new HKT rules
- **Breaking**: removes all old interfaces from `primitives/interfaces.py`,
  use new typeclasses instead
- **Breaking**: ``Maybe`` is fully reworked to be lawful
- **Breaking**: removes `value_or` pointfree method,
  because it is impossible to express with HKT
- **Breaking**: removes `.value_or`, `.unwrap`, and `.failure` methods
  from `FutureResult` and `RequiresContext`-based types,
  because we do require these methods to raise an exception on failure,
  but these methods were lazy and did not raise the required exception
- **Breaking**: changes how `is_successful` is typed:
  now we allow any `Unwrappable` interface instances there,
  including custom ones
- **Breaking**: changes `UnwrapFailedError` constructor,
  now it does accept an `Unwrappable` instance instead of a `BaseContainer`
- **Breaking**: removes `.fix` method from all containers,
  also removes `fix` pointfree function
- **Breaking**: removes `unify` poinfree function,
  it is not a recommeneded way to compose things,
  but due to HKT support,
  users can write their own `unify` poinfree function now
- **Breaking**: Removes `coalesce` function,
  because it is impossible to properly type it
- **Breaking**: Removes all `Context*` based types with `.ask()` method,
  use new `.ask()` methods on the `Reader`-based containers
- **Breaking**: Now `Future` and `FutureResult` can be awaited multiple times

- Adds new public interfaces: see `returns.interfaces`
- Adds `methods` package with all the composition methods we support
- Adds better `from_iterable` support,
  now it receives a custom strategy with how to handle iterable
- Adds two predefined iterable strategies: `FailFast` and `CollectAll`

- Adds `FutureSuccess` and `FutureFailure` unit functions
  to be similar to `Result` and `IOResult`
- Adds `.swap` method to `Result`, `IOResult`, `FutureResult`,
  and other result based containers
- Adds `.modify_env` method to all `RequiresContext*` types
- Adds `.rescue` to `Maybe`
- Adds `.equals` methods to types that can be compared directly:
  `Result`, `Maybe`, `IO`, `IOResult`
- Adds missing `from_requires_context_future_result` to `RequiresContext`
- Adds `.from_optional` and `.bind_optional` to `Maybe` container
- Adds `__slots__` to `UnwrapFailedError` with `halted_container`
- Changes `flatten` to work with `KindN` and any possible container
- Changes `iterable` helper function to be `iterable_kind`,
  now it works with any `KindN`
- Adds a helper to test traces to our `pytest` plugin
- Adds `cond` method to `methods` package
- Adds `cond` function to `pointfree` package
- Adds `compose_result` HKT method and pointfree function
- Adds `unify` HKT method and pointfree function

- Adds `collect_trace` helper function for better development experience
- Adds `hypothesis` intergration and pre-defined "monad laws as values"

### Bugfixes

- **Breaking**: fixes serious typing issue and changes how `flow` works,
  now it has a hard limit of 21 parameters: 1 instance + 20 functions
- **Breaking**: fixes serious typing issue and changes how `pipe` works,
  now it has a hard limit of 20 parameters
- Fixes that `RequiresContextFutureResult` was not supported by `pytest` plugin

### Misc

- Adds a lot of new typetests
- Checks that now all math laws are checked for all types
- Changes docs structure, adds new `Interfaces`, `HKT`, and `Methods` pages


## 0.14.0

### Features

- **Breaking**: renames mypy plugin from `decorator_plugin` to `returns_plugin`
  because of a complete rewrite and lots of new features
- **Breaking**: changes `@safe`, `@impure`, `impure_safe`, `@maybe` semantics:
  they do not work with `async` functions anymore;
  now you are forced to use `Future` and its helpers
  to work with `async` functions
- **Breaking**: renames `Maybe.new` to `Maybe.from_value`.
  Because all our other containers support this protocol.
  Only `Maybe` was different, sorry for that!
- **Breaking**: renames `.from_success()` to `.from_value()`,
  there's no need in two separate methods
- **Breaking**: renames `.from_successful_io()` to `.from_io()`,
  there's no need in two separate methods
- **Breaking**: renames `.from_successful_context()` to `.from_context()`,
  there's no need in two separate methods
- **Breaking**: since we now support `.apply()` method,
  there's no more need in `*_squash` converters, they are removed
- **Breaking**: renamed `Instanceable` to `Applicative`
- **Breaking**: changes `.from_io` and `.from_failed_io` of `IOResult`
  to return `Any` instead of `NoReturn` unfilled type
- **Breaking**: removes `.lift` and `.lift_*` methods from all containers,
  use `map_`, `bind_result`, `bind_io`, and other pointfree helpers instead
- **Breaking**: removes `@pipeline` function. It was a mistake:
  it does not work with mixed container types,
  it does not type failures properly,
  it does not work with ``IO`` and ``Future``,
  it enforces to write imperative code in a functional codebase.
  Use ``flow`` instead

- Adds typed `partial` and `curry` mypy plugins!
- Adds typed `flow` plugin, now it can accept any number of arguments,
  it now also has **excelent** type inference
- Adds typed `pipe` plugin, now it can accept any number of arguments,
  it now also has good type inference
- Adds `managed` pipeline function that is useful
  for working with stateful computations

- Adds typed `map_`, `fix`, and `alt` pointfree functions
- Adds typed `bind_result`, `bind_io`, `bind_ioresult`,
  `bind_context`, `bind_context_result`, `bind_future`,
  `bind_async`, and `bind_awaitable` pointfree functions
- Adds typed `bind_async_future` and `bind_async_future_result`
  pointfree functions
- Adds typed `unify` pointfree function
- Adds typed `apply` pointfree function
- Adds typed `value_or` pointfree function

- Adds `pytest` plugin with the ability to tests error handling

- Adds `Future` container to easily work with `async` functions
- Adds `FutureResult` container to easily work
  with `async` function that might fail
- Adds `RequiresContextFutureResult` container
- Adds `ReaderFutureResult` alias for `RequiresContextFutureResult`
- Adds `RequiresContextFutureResultE` and `ReaderFutureResultE` aliases
- Adds `Future`, `FutureResult` and `RequiresContextFutureResult`
  support for all existing pointfree functions

- Adds `bind_io` method to `IOResult`
- Adds `bind_io` method to `RequiresContextIOResult`
- Adds `or_else` method to `Maybe`
- Adds `.from_io` and `.from_failed_io` to `RequiresContextIOResult`

- Syncs naming in `from_*` methods, now all parameters are named `inner_value`
- Adds `not_` composition helper
- Adds `flatten` support for `Future`,
  `FutureResult` and `RequiresContextFutureResult`
- Adds `__copy__` and `__deepcopy__` magic methods to `Immutable` class
- Speeds up ``is_successful`` function
- Makes all `Context` context helpers abstract,
  so you cannot create new instances of this class,
  also adds `__slots__` to these classes
- Improves `RequiresContext*` types with `NoDeps` where it is logically true

### Bugfixes

- Fixes that `@safe` decorator was generating incorrect signatures
  for functions with `Any`
- Fixes that `.rescue()` of `RequiresContextResult` was returning `Any`
- Fixes that `.rescue()` of `RequiresContextIOResult` was returning `Any`
- Fixes that `RequiresContextResult` and `RequiresContextIOResult`
  were not `final`
- Fixes that `ImmutableStateError` was not a subclass of `AttributeError`
- Fixes that `IOResult` was not showing `str` representation
  of wrapped `inner_value`

### Misc

- Replaces `pytest-asyncio` with `anyio` plugin,
  now we test compatibility with any IO stack: `asyncio`, `trio`, `curio`
- Updates lots of dependencies
- Adds lots of new tests
- Updates lots of docs
- Removes "IO marker" name from docs in favor for "IO container",
  it is not special at all. Why would we call it differently?


## 0.13.0

### Features

- **Breaking**: renames `join` to `flatten`, sorry!
- **Breaking**: renames `box` to `bind` and moves it to `returns.pointfree`
- **Breaking**: removes `Maybe.rescue` and `Maybe.fix` methods
- **Breaking**: renames `io_squash` to `squash_io`
  and moves it to `returns.converters`
- **Breaking**: moves all interfaces from `returns.primitives.container` to
  `returns.primitives.interfaces`

- Adds `rescue` pointfree function
- Adds `ResultE` alias for `Result[..., Exception]`

- Adds `RequiresContext` container and `Context` helper class
- Adds `RequiresContext` support for `bind` pointfree function
- Adds `RequiresContext` support for `flatten` function

- Adds `RequiresContextResult` container
- Adds `RequiresContextResultE` alias
- Adds `ReaderResult` and `ReaderResultE` aliases
  for `RequiresContextResult[..., ..., Exception]`
- Adds `RequiresContextResult` support for `bind` and `rescue`
- Adds `RequiresContextResult` support for `flatten`

- Adds `IOResult` helper to work better with `IO[Result[a, b]]`
- Adds `IOResultE` alias for `IOResult[a, Exception]`
- Adds `IOResult` support for `bind`
- Adds `IOResult` support for `flatten`
- Adds `IOResult` support for `@pipeline`
- Adds `IOResult` support for `coalesce`
- Adds `IOResult` support for `is_successful`

- Adds `RequiresContextIOResult` container
- Adds `RequiresContextIOResultE` alias
- Adds `ReaderIOResult` and `ReaderIOResultE` aliases
  for `RequiresContextIOResult[..., ..., Exception]`
- Adds `RequiresContextIOResult` support for `bind` and `rescue`
- Adds `RequiresContextIOResult` support for `flatten`

- Adds `Result.lift`, `Maybe.lift`, `RequiresContext.lift`,
  and `RequiresContextResult.lift` functions in addition to `IO.lift`

- Adds `Immutable` primitive type
- Adds `Unitable` protocol and `.from_success()` and `.from_failure()`
  methods for all `Result` related classes
- Adds `Instanceable` protocol and `.from_value()` method
  for `IO` and `RequiresContext`

- Adds `flow` function, which is similar to `pipe`
- Adds `swap` converter for `Result` and `IOResult`
- Adds `squash_context` function to squash `RequiresContext` similar to `IO`

### Bugfixes

- Now `Success` and `Failure` (both `io` and pure) return `Any` and not `NoReturn`
- Fixes how `flatten` works, also adds more tests and docs about `Failure` case
- Fixes `Unwrappable` type being parametrized with only one `TypeVar`
- Changes `Success` and `Failure` to return `Any` instead of `NoReturn`

### Misc

- Updates `poetry` version in `travis`
- Imporves ``pipe`` docs with ``lambda`` and `Generic` problem
- Improves docs in several places
- Now examples in docs tries to be docstests where possible
- Changes how tests are checked with `mypy` in CI


## 0.12.0

### Features

- **Breaking**: now `@pipeline` requires a container type when created:
  `@pipeline(Result)` or `@pipeline(Maybe)`
- `Maybe` and `Result` now has `success_type` and `failure_type` aliases
- Adds `Result.unify` utility method for better error type composition
- We now support `dry-python/classes` as a first-class citizen
- Adds `io_squash` to squash several `IO` containers into one container
  with a tuple inside, currently works with `9` containers max at a time
- Adds `untap` function which does convert return type to `None`

### Bugfixes

- Fixes that containers were not usable with `multiprocessing`
- Changes the inheritance order, now `BaseContainer` is the first child
- Fixes that `Nothing` had incorrect docstrings

### Misc

- Now `generated` package is protected
- Updates `poetry` to `1.0`


## 0.11.0

### Features

- **Breaking**: now `pipe()` does not require argument to be the first value,
  instead it is required to use: `pipe(f1, f2, f3, f4)(value)`
- **Breaking**: dropped everything from `returns/__init__.py`,
  because we now have quite a lot of stuff
- **Breaking**: dropped support of zero argument functions for `Nothing.fix`
- **Breaking**: dropped support of zero argument functions for `Nothing.rescue`
- `Maybe` now has `.failure()` to match the same API as `Result`
- Adds `identity` function
- Adds `tap` function
- Now `pipe` allows to pipe 8 steps
- Adds `coalesce_result` and `coalesce_maybe` converters

### Bugfixes

- Fixes that code inside `.fix` and `.rescue` of `Maybe` might be called twice

### Misc

- Now all methods have doctests
- Updates docs about `Success` and `_Success`, `Failure` and `_Failure`
- Updates docs about `@pipeline`
- Typechecks async functions and decorators inside `typesafety/` tests


## 0.10.0

### Features

- **Breaking**: `python>=3.7,<=3.7.2` are not supported anymore,
  because of a bug inside `typing` module
- **Breaking**: Now `bind` does not change the type of an error
- **Breaking**: Now `rescue` does not change the type of a value
- **Breaking**: Renames `map_failure` to `alt`
- Adds `box()` function with the ability
  to box function for direct container composition like:
  `a -> Container[b]` to `Container[a] -> Container[b]`
- Adds `IO.lift()` function to lift `a -> a` to `IO[a] -> IO[a]`
- Adds `pipe()` function to `pipeline.py`
- Adds `__hash__()` magic methods to all containers

### Bugfixes

- Changes `Any` to `NoReturn` in `Success` and `Failure`
- Now all type parameters in `Result`, `Maybe`, and `IO` are covariant

### Misc

- Massive docs rewrite
- Updates `mypy` version
- Updates `wemake-python-styleguide` and introduces `nitpick`
- Updates `pytest-plugin-mypy`, all tests now use `yml`


## 0.9.0

### Features

- Provides a bunch of primitive interfaces to write your own containers
- Adds `.map_failure()` method
- Adds `flatten()` function to join nested containers

### Bugfixes

- Fixes type of `Maybe.fix` and `Maybe.rescue` to work with both `lambda: 1` and `lambda _: 1`

### Misc

- Improves `README`


## 0.8.0

### Features

- Reintroduces the `Maybe` container, typed!
- Introduces converters from one type to another
- Adds `mypy` plugin to type decorators
- Complete rewrite of `Result` types
- Partial API change, now `Success` and `Failure` are not types, but functions
- New internal types introduced: `FixableContainer` and `ValueUnwrapContainer`

### Bugfixes

- Fixes issue when you could return `IO` container from `Result.bind`
- Fixes `@pipeline` return type

### Misc

- Reapplied all types to `.py` files
- Improved docs about `IO` and `Container` concept
- Adds docs about container composition
- Moves from `Alpha` to `Beta`


## 0.7.0

### Features

- Adds `IO` container
- Adds `unsafe` module with unsafe functions
- Changes how functions are located inside the project

### Bugfixes

- Fixes container type in `@pipeline`
- Now `is_successful` is public
- Now `raise_exception` is public

### Misc

- Changes how `str()` function works for container types
- Total rename to "container" in the source code


## Version 0.6.0

### Features

- `safe` and `pipeline` now supports `asyncio`
- `is_successful` now returns `Literal` types if possible


## Version 0.5.0

### Features

- Adds `compose` helper function
- Adds public API to `import returns`
- Adds `raise_exception` helper function
- Adds full traceback to `.unwrap()`


### Misc

- Updates multiple dev-dependencies, including `mypy`
- Now search in the docs is working again
- Relicenses this project to `BSD`
- Fixes copyright notice in the docs


## Version 0.4.0 aka Goodbye, containers!

### Features

- Moves all types to `.pyi` files
- Renames all classes according to new naming pattern
- **HUGE** improvement of types
- Renames `fmap` to `map`
- Renames `do_notation` to `pipeline`, moves it to `functions.py`
- Renames `ebind` to `rescue`
- Renames `efmap` to `fix`
- Renames `container` to `Container`
- Removes `Maybe` container, since typing does not have `NonNullable` type


## Version 0.3.1

### Bugfixes

- Adds `py.typed` file to be `PEP561` compatible


## Version 0.3.0, Renamed to `returns`

The project is renamed to `returns` and moved to `dry-python` org.

### Features

- Adds `.pyi` files for all modules,
  to enable `mypy` support for 3rd party users


## Version 0.2.0

### Features

- Adds `Maybe` container
- Adds immutability and `__slots__` to all containers
- Adds methods to work with failures
- Adds `safe` decorator to convert exceptions to `Result` container
- Adds `is_successful()` function to detect if your result is a success
- Adds `failure()` method to unwrap values from failed containers

### Bugfixes

- Changes the type of `.bind` method for `Success` container
- Changes how equality works, so now `Failure(1) != Success(1)`
- Changes how new instances created on unused methods

### Misc

- Improves docs


## Version 0.1.1

### Bugfixes

- Changes how `PyPI` renders package's page

### Misc

- Improves `README` with new badges and installation steps


## Version 0.1.0

Initial release. Featuring only `Result` and `do_notation`.
