# returns

[![Returns logo](https://raw.githubusercontent.com/dry-python/brand/master/logo/returns.png)](https://github.com/dry-python/returns)

-----

[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services) [![Build Status](https://travis-ci.org/dry-python/returns.svg?branch=master)](https://travis-ci.org/dry-python/returns) [![Coverage Status](https://coveralls.io/repos/github/dry-python/returns/badge.svg?branch=master)](https://coveralls.io/github/dry-python/returns?branch=master) [![Documentation Status](https://readthedocs.org/projects/returns/badge/?version=latest)](https://returns.readthedocs.io/en/latest/?badge=latest) [![Python Version](https://img.shields.io/pypi/pyversions/returns.svg)](https://pypi.org/project/returns/) [![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)

-----

Make your functions return something meaningful, typed, and safe!


## Features

- Provides a bunch of primitives to write declarative business logic
- Enforces [Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/)
- Fully typed with annotations and checked with `mypy`,
  allowing you to write type-safe code as well, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Pythonic and pleasant to write and to read (!)


## Installation


```bash
pip install returns
```

Make sure you know how to get started, [check out our docs](https://returns.readthedocs.io/en/latest/)!


## Why?

Consider this code that you can find in **any** `python` project.

### Straight-forward approach

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
from returns.functions import pipeline, safe
from returns.result import Result

class FetchUserProfile(object):
    """Single responsibility callable object that fetches user profile."""

    #: You can later use dependency injection to replace `requests`
    #: with any other http library (or even a custom service).
    _http = requests

    @pipeline
    def __call__(self, user_id: int) -> Result['UserProfile', Exception]:
        """Fetches UserProfile dict from foreign API."""
        response = self._make_request(user_id).unwrap()
        return self._parse_json(response)

    @safe
    def _make_request(self, user_id: int) -> requests.Response:
        response = self._http.get('/api/users/{0}'.format(user_id))
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
If the result is `Failure[Exception]` we will actually raise an exception at this point.
But it is safe to use `.unwrap()` inside [@pipeline](https://returns.readthedocs.io/en/latest/pages/functions.html#returns.functions.pipeline)
functions.
Because it will catch this exception and wrap it inside a new `Failure[Exception]`!

And we can clearly see all result patterns that might happen in this particular case:
- `Success[UserProfile]`
- `Failure[HttpException]`
- `Failure[JsonDecodeException]`

And we can work with each of them precisely.

What more? [Go to the docs!](https://returns.readthedocs.io)

## License

MIT.
