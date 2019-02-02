# Version history

We follow Semantic Versions since the `0.1.0` release.

## Version 0.3.0, Renamed to `returns`

The project is renamed to `returns` and moved to `dry-python` org.

### Features

- Adds `.pyi` files for all modules,
  to enable `mypy` support for 3rd party users


## Version 0.2.0

### Features

- Adds `Maybe` monad
- Adds immutability and `__slots__` to all monads
- Adds methods to work with failures
- Adds `safe` decorator to convert exceptions to `Either` monad
- Adds `is_successful()` function to detect if your result is a success
- Adds `failure()` method to unwrap values from failed monads

### Bugfixes

- Changes the type of `.bind` method for `Success` monad
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
