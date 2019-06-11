[![Returns logo](https://raw.githubusercontent.com/dry-python/brand/master/logo/returns.png)](https://github.com/dry-python/returns)

-----

[![Build Status](https://travis-ci.org/dry-python/returns.svg?branch=master)](https://travis-ci.org/dry-python/returns) [![Coverage Status](https://coveralls.io/repos/github/dry-python/returns/badge.svg?branch=master)](https://coveralls.io/github/dry-python/returns?branch=master) [![Documentation Status](https://readthedocs.org/projects/returns/badge/?version=latest)](https://returns.readthedocs.io/en/latest/?badge=latest) [![Python Version](https://img.shields.io/pypi/pyversions/returns.svg)](https://pypi.org/project/returns/) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

-----

Make your functions return something meaningful, typed, and safe!


## Features

- Provides a bunch of primitives to write declarative business logic
- Enforces better architecture
- Fully typed with annotations and checked with `mypy`, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Pythonic and pleasant to write and to read (!)
- Support functions and coroutines, framework agnostic


## Installation

```bash
pip install returns
```

Make sure you know how to get started, [check out our docs](https://returns.readthedocs.io/en/latest/)!


## Contents

- [Result container](#result-container) that let's you to get rid of exceptions
- [IO marker](#io-marker) that marks all impure operations and structures them


## Result container

Please, make sure that you are also aware of
[Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/).

### Straight-forward approach

Consider this code that you can find in **any** `python` project.

```python
import requests

def fetch_user_profile(user_id: int) -> 'UserProfile':
    """Fetches UserProfile dict from foreign API."""
    response = requests.get('/api/users/{0}'.format(user_id))
    response.raise_for_status()
    return response.json()
```

Seems legit, does not it?
It also seems like a pretty straight forward code to test.
All you need is to mock `requests.get` to return the structure you need.

But, there are hidden problems in this tiny code sample
that are almost impossible to spot at the first glance.

### Hidden problems

Let's have a look at the exact same code,
but with the all hidden problems explained.

```python
import requests

def fetch_user_profile(user_id: int) -> 'UserProfile':
    """Fetches UserProfile dict from foreign API."""
    response = requests.get('/api/users/{0}'.format(user_id))

    # What if we try to find user that does not exist?
    # Or network will go down? Or the server will return 500?
    # In this case the next line will fail with an exception.
    # We need to handle all possible errors in this function
    # and do not return corrupt data to consumers.
    response.raise_for_status()

    # What if we have received invalid JSON?
    # Next line will raise an exception!
    return response.json()
```

Now, all (probably all?) problems are clear.
How can we be sure that this function will be safe
to use inside our complex business logic?

We really can not be sure!
We will have to create **lots** of `try` and `except` cases
just to catch the expected exceptions.

Our code will become complex and unreadable with all this mess!

### Pipeline example

```python
import requests
from returns.result import Result, pipeline, safe

class FetchUserProfile(object):
    """Single responsibility callable object that fetches user profile."""

    @pipeline
    def __call__(self, user_id: int) -> Result['UserProfile', Exception]:
        """Fetches UserProfile dict from foreign API."""
        response = self._make_request(user_id).unwrap()
        return self._parse_json(response)

    @safe
    def _make_request(self, user_id: int) -> requests.Response:
        response = requests.get('/api/users/{0}'.format(user_id))
        response.raise_for_status()
        return response

    @safe
    def _parse_json(self, response: requests.Response) -> 'UserProfile':
        return response.json()
```

Now we have a clean and a safe way to express our business need.
We start from making a request, that might fail at any moment.

Now, instead of returning a regular value
it returns a wrapped value inside a special container
thanks to the
[@safe](https://returns.readthedocs.io/en/latest/pages/functions.html#returns.functions.safe)
decorator.

It will return [Success[Response] or Failure[Exception]](https://returns.readthedocs.io/en/latest/pages/result.html).
And will never throw this exception at us.

When we will need raw value, we can use `.unwrap()` method to get it.
If the result is `Failure[Exception]`
we will actually raise an exception at this point.
But it is safe to use `.unwrap()` inside
[@pipeline](https://returns.readthedocs.io/en/latest/pages/functions.html#returns.functions.pipeline)
functions.
Because it will catch this exception
and wrap it inside a new `Failure[Exception]`!

And we can clearly see all result patterns
that might happen in this particular case:
- `Success[UserProfile]`
- `Failure[HttpException]`
- `Failure[JsonDecodeException]`

And we can work with each of them precisely.
It is a good practice to create `Enum` classes or `Union` types
with a list of all the possible errors.


## IO marker

But is that all we can improve?
Let's look at `FetchUserProfile` from another angle.
All its methods look like regular ones:
it is impossible to tell whether they are pure or impure from the first sight.

It leads to a very important consequence:
*we start to mix pure and impure code together*.
We should not do that!

When these two concepts are mixed
we suffer really bad when testing or reusing it.
Almost everything should be pure by default.
And we should explicitly mark impure parts of the program.

### Explicit IO

Let's refactor it to make our
[IO](https://returns.readthedocs.io/en/latest/pages/io.html) explicit!

```python
import requests
from returns.io import IO, impure
from returns.result import Result, pipeline, safe

class FetchUserProfile(object):
    """Single responsibility callable object that fetches user profile."""

    @pipeline
    def __call__(self, user_id: int) -> Result[IO['UserProfile'], Exception]]:
        """Fetches UserProfile dict from foreign API."""
        response = self._make_request(user_id).unwrap()
        return self._parse_json(response)

    @safe
    @impure
    def _make_request(self, user_id: int) -> requests.Response:
        response = requests.get('/api/users/{0}'.format(user_id))
        response.raise_for_status()
        return response

    @safe
    def _parse_json(
        self,
        io_response: IO[requests.Response],
    ) -> IO['UserProfile']:
        return io_response.map(lambda response: response.json())
```

Now we have explicit markers where the `IO` did happen
and these markers cannot be removed.

Whenever we access `FetchUserProfile` we now know
that it does `IO` and might fail.
So, we act accordingly!

## More!

Want more? [Go to the docs!](https://returns.readthedocs.io)
Or read these articles:

- [Python exceptions considered an anti-pattern](https://sobolevn.me/2019/02/python-exceptions-considered-an-antipattern)
- [Enforcing Single Responsibility Principle in Python](https://sobolevn.me/2019/03/enforcing-srp)
