# How to contribute

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

To install them you would need to run `install` command:

```bash
poetry install
```

To activate your `virtualenv` run `poetry shell`.


## Tests

We use `pytest` and `flake8` for quality control.
We also use `wemake_python_styleguide` to enforce the code quality.

To run all tests:

```bash
pytest . docs/pages
```

To run linting:

```bash
flake8 .
```
Keep in mind: default virtual environment folder excluded by flake8 style checking is `.venv`.
If you want to customize this parameter, you should do this in `setup.cfg`.

These steps are mandatory during the CI.

### Type tests

We also `pytest-mypy-plugins`. Tests cases are located inside `./typesafety`
If you create new types or typed functions, it is required to test their types.
Here's [a tutorial](https://sobolevn.me/2019/08/testing-mypy-types) on how to do that.


## Type checks

We use `mypy` to run type checks on our code.
To use it:

```bash
mypy returns tests/**/*.py
```

This step is mandatory during the CI.


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

1. Run `pytest` to make sure everything was working before
2. Add any changes you want
3. Add tests for the new changes
4. Edit documentation if you have changed something significant
5. Update `CHANGELOG.md` with a quick summary of your changes
6. Run `pytest` again to make sure it is still working
7. Run `mypy` to ensure that types are correct
8. Run `flake8` to ensure that style is correct
9. Run `doc8` to ensure that docs are correct


## Other help

You can contribute by spreading a word about this library.
It would also be a huge contribution to write
a short article on how you are using this project.
You can also share your best practices with us.
