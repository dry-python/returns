# Version history

We follow Semantic Versions since the `0.1.0` release.

## Version 0.2.0

### Features

- Adds `Maybe` monad
- Adds immutability and `__slots__` to all monads
- Adds `__hash__` support for immutable inner values
- Adds methods to work with failures
- Adds `safe` decorator to convert exceptions to `Either` monad
- Adds `is_successful()` function to detect if your result is a success

### Bugfixes

- Changes the type of `.bind` method for `Success` monad

### Misc

- Improves docs


## Version 0.1.1

### Bugfixes

- Changes how `PyPI` renders package's page

### Misc

- Improves `README` with new badges and installation steps


## Version 0.1.0

Initial release. Featuring only `Result` and `do_notation`.
