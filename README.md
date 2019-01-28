# dry-monads

[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services) [![Build Status](https://travis-ci.org/sobolevn/dry-monads.svg?branch=master)](https://travis-ci.org/sobolevn/dry-monads) [![Coverage Status](https://coveralls.io/repos/github/sobolevn/dry-monads/badge.svg?branch=master)](https://coveralls.io/github/sobolevn/dry-monads?branch=master) [![Documentation Status](https://readthedocs.org/projects/dry-monads/badge/?version=latest)](https://dry-monads.readthedocs.io/en/latest/?badge=latest) [![Python Version](https://img.shields.io/pypi/pyversions/dry-monads.svg)](https://pypi.org/project/dry-monads/) [![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/sobolevn/dry-monads/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot) [![dry-monads](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/sobolevn/dry-monads)


Monads for `python` made simple and safe.


## Features

- Provides primitives to write declarative business logic
- Fully typed with annotations and checked with `mypy`,
  allowing you to write type-safe code as well
- No operator overloading or other unpythonic stuff that makes your eyes bleed


## Installation


```bash
pip install dry-monads
```


## What's inside?

We have several the most iconic monads inside:

- [Result, Failure, and Success](https://dry-monads.readthedocs.io/en/latest/pages/either.html) (also known as `Either`, `Left`, and `Right`)
- `Maybe`, `Some`, and `Nothing` (currently WIP)
- `Just` (currently WIP)

We also care about code readability and developer experience,
so we have included some useful features to make your life easier:

- [Do notation](https://dry-monads.readthedocs.io/en/latest/pages/do-notation.html)


## Example


```python
from dry_monads.do_notation import do_notation
from dry_monads.either import Result, Success, Failure

class CreateAccountAndUser(object):
    """Creates new Account-User pair."""

    @do_notation
    def __call__(self, username: str, email: str) -> Result['User', str]:
        """Can return a Success(user) or Failure(str_reason)."""
        user_schema = self._validate_user(username, email).unwrap()
        account = self._create_account(user_schema).unwrap()
        return self._create_user(account)

    # Protected methods
    # ...

```

We are [covering what's going on in this example](https://dry-monads.readthedocs.io/en/latest/pages/do-notation.html) in the docs.

## Inspirations

This module is heavily based on:

- [dry-rb/dry-monads](https://github.com/dry-rb/dry-monads)
- [Ø](https://github.com/dbrattli/OSlash)
- [pymonad](https://bitbucket.org/jason_delaat/pymonad)
