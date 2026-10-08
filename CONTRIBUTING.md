# How to contribute

Do you have questions or issues? Join our chat!

[![Telegram chat](https://img.shields.io/badge/chat-join-blue?logo=telegram)](https://t.me/drypython)

## Tutorials

If you want to start working on this project,
you will need to get familiar with these concepts:

- http://learnyouahaskell.com/functors-applicative-functors-and-monoids
- https://github.com/dbrattli/OSlash/wiki/Functors,-Applicatives,-And-Monads-In-Pictures
- https://gcanti.github.io/fp-ts/ and https://dev.to/gcanti

Here are some practical examples of what we are doing here:

- https://medium.com/@rnesytov/using-Result-monad-in-python-b6eac698dff5
- https://www.morozov.is/2018/09/08/monad-laws-in-ruby.html
- https://beepb00p.xyz/mypy-error-handling.html


## Dependencies

We use [`poetry`](https://github.com/python-poetry/poetry) to manage the dependencies.

To install them you would need to run the `install` command:

```bash
poetry install
```

To install extra dependencies for working on the `hypothesis` or `mypy` plugin:

```bash
poetry install --extras check-laws
poetry install --extras compatible-mypy
```

To activate your `virtualenv` run `eval $(poetry env activate)`.


## Makefile

To make local development easier, all common commands are available
via the [`Makefile`](Makefile). Run `make help` to see all available targets:

```bash
make help
```

Main targets:

- `make format` — format and autofix code with `ruff`
- `make lint` — run all linting checks (`ruff` and `flake8`)
- `make type-check` — run `mypy` type checks
- `make unit` — run standard tests with `pytest`
- `make typesafety` — run type-safety tests (`pytest-mypy-plugins`)
- `make slots` — check `__slots__` correctness with `slotscheck`
- `make package` — check package dependencies with `pip check`
- `make test` — run all checks: lint, type-check, unit tests, slots, and package


## Tests

We use `pytest` and `flake8` for quality control.
We also use `wemake_python_styleguide` and `ruff` to enforce code quality.

To run standard tests:

```bash
poetry run pytest returns docs/pages tests
```

Or simply:

```bash
make unit
```

**NOTE:** type-safety tests not included, see section on type tests below

To run linting:

```bash
poetry run flake8 .
poetry run ruff check --exit-non-zero-on-fix
poetry run ruff format --check --diff
```

Or simply:

```bash
make lint
```

Keep in mind: default virtual environment folder excluded by flake8 style checking is `.venv`.
If you want to customize this parameter, you should do this in `setup.cfg`.

These steps are mandatory during CI.

### Pre-commit hooks

We use [`pre-commit`](https://pre-commit.com/) to run some checks
automatically before each commit. Among others, it runs `ruff check`
and `ruff format` on the changed files.

To install the hooks, run:

```bash
poetry run pre-commit install
```

To run all hooks manually:

```bash
poetry run pre-commit run --all-files
```

### Type tests

We also use `pytest-mypy-plugins`. Tests cases are located inside `./typesafety`
If you create new types or typed functions, it is required to test their types.

The type-safety tests can be run with the following:

```bash
poetry run pytest typesafety
```

Or simply:

```bash
make typesafety
```

**NOTE:** This can take upwards of 20 minutes, only recommended to run if necessary.

Here's [a helpful tutorial](https://sobolevn.me/2019/08/testing-mypy-types) if you are looking
for more information.


## Type checks

We use `mypy` to run type checks on our code.
To use it:

```bash
poetry run mypy returns
poetry run mypy docs tests
```

Or simply:

```bash
make type-check
```

This step is mandatory during CI.


## Submitting your code

We use [trunk based](https://trunkbaseddevelopment.com/)
development (we also sometimes call it `wemake-git-flow`).

What the point of this method?

1. We use protected `master` branch,
   so the only way to push your code is via pull request
2. We use issue branches: to implement a new feature or to fix a bug
   create a new branch named `issue-$TASKNUMBER`
3. Then create a pull request to `master` branch
4. We use `git tag`s to make releases, so we can track what has changed
   since the latest release

So, this way we achieve an easy and scalable development process
which frees us from merging hell and long-living branches.

In this method, the latest version of the app is always in the `master` branch.

### Before submitting

Before submitting your code please do the following steps:

1. Run `make unit` (or `pytest`) to make sure everything was working before
2. Add any changes you want
3. Add tests for the new changes
4. Edit documentation if you have changed something significant
5. Update `CHANGELOG.md` with a quick summary of your changes
6. Run `make format` to format the code with `ruff`
7. Run `make test` to run all checks: linting (`ruff`, `flake8`),
   `mypy` types, `pytest` tests, `slotscheck`, and `pip check`


## Other help

You can contribute by spreading a word about this library.
It would also be a huge contribution to write
a short article on how you are using this project.
You can also share your best practices with us.

Join in the conversation with us on our Telegram.
[![Telegram chat](https://img.shields.io/badge/chat-join-blue?logo=telegram)](https://t.me/drypython)
