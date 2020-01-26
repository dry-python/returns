[![Returns logo](https://raw.githubusercontent.com/dry-python/brand/master/logo/returns.png)](https://github.com/dry-python/returns)

-----

[![Build Status](https://travis-ci.com/dry-python/returns.svg?branch=master)](https://travis-ci.com/dry-python/returns)
[![Coverage Status](https://coveralls.io/repos/github/dry-python/returns/badge.svg?branch=master)](https://coveralls.io/github/dry-python/returns?branch=master)
[![Documentation Status](https://readthedocs.org/projects/returns/badge/?version=latest)](https://returns.readthedocs.io/en/latest/?badge=latest)
[![Python Version](https://img.shields.io/pypi/pyversions/returns.svg)](https://pypi.org/project/returns/)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

-----

Make your functions return something meaningful, typed, and safe!


## Features

- Provides a bunch of primitives to write declarative business logic
- Enforces better architecture
- Fully typed with annotations and checked with `mypy`, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)
- Has a bunch of helpers for better composition
- Pythonic and pleasant to write and to read (!)
- Support functions and coroutines, framework agnostic
- Easy to start: has lots of docs, tests, and tutorials


## Installation

```bash
pip install returns
```

You might also want to [configure](https://returns.readthedocs.io/en/latest/pages/container.html#type-safety)
`mypy` correctly and install our plugin
to fix [this existing issue](https://github.com/python/mypy/issues/3157):

```ini
# In setup.cfg or mypy.ini:
[mypy]
plugins =
  returns.contrib.mypy.decorator_plugin
```

We also recommend to use the same `mypy` settings [we use](https://github.com/wemake-services/wemake-python-styleguide/blob/master/styles/mypy.toml).

Make sure you know how to get started, [check out our docs](https://returns.readthedocs.io/en/latest/)!


## Contents

- [Maybe container](#maybe-container) that allows you to write `None`-free code
- [RequiresContext container](#requirescontext-container) that allows you to use typed functional dependency injection
- [Result container](#result-container) that let's you to get rid of exceptions
- [IO marker](#io-marker) and [IOResult](#troublesome-io) that marks all impure operations and structures them


## Maybe container

`None` is called the [worst mistake in the history of Computer Science](https://www.infoq.com/presentations/Null-References-The-Billion-Dollar-Mistake-Tony-Hoare/).

So, what can we do to check for `None` in our programs?
You can use builtin [Optional](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#optional-types-and-the-none-type) type
and write a lot of `if some is not None:` conditions.
But, **having `null` checks here and there makes your code unreadable**.

```python
user: Optional[User]

if user is not None:
     balance = user.get_balance()
     if balance is not None:
         balance_credit = balance.credit_amount()
         if balance_credit is not None and balance_credit > 0:
             can_buy_stuff = True
else:
    can_buy_stuff = False
```

Or you can use
[Maybe](https://returns.readthedocs.io/en/latest/pages/maybe.html) container!
It consists of `Some` and `Nothing` types,
representing existing state and empty (instead of `None`) state respectively.

```python
from typing import Optional
from returns.maybe import Maybe, maybe

@maybe  # decorator to convert existing Optional[int] to Maybe[int]
def bad_function() -> Optional[int]:
    ...

maybe_result: Maybe[float] = bad_function().map(
    lambda number: number / 2,
)
# => Maybe will return Some[float] only if there's a non-None value
#    Otherwise, will return Nothing
```

You can be sure that `.map()` method won't be called for `Nothing`.
Forget about `None`-related errors forever!

And that's how your initial refactored code will look like:

```python
user: Optional[User]

can_buy_stuff: Maybe[bool] = Maybe.new(user).map(  # type hint is not required
    lambda real_user: real_user.get_balance(),
).map(
    lambda balance: balance.credit_amount(),
).map(
    lambda balance_credit: balance_credit > 0,
)
```

Much better, isn't it?


## RequiresContext container

Many developers do use some kind of [dependency injection](https://github.com/dry-python/dependencies) in Python.
And usually it is based on the idea
that there's some kind of a container and assembly process.

Functional approach is much simplier!

Imagine that you have a `django` based game, where you award users with points for each guessed letter in a word (unguessed letters are marked as `'.'`):

```python
from django.http import HttpRequest, HttpResponse
from words_app.logic import calculate_points

def view(request: HttpRequest) -> HttpResponse:
    user_word: str = request.GET['word']  # just an example
    points = calculate_points(user_word)
    ...  # later you show the result to user somehow

# Somewhere in your `words_app/logic.py`:

def calculate_points(word: str) -> int:
    guessed_letters_count = len([letter for letter in word if letter != '.'])
    return _award_points_for_letters(guessed_letters_count)

def _award_points_for_letters(guessed: int) -> int:
    return 0 if guessed < 5 else guessed  # minimum 6 points possible!
```

Awesome! It works, users are happy, your logic is pure and awesome.
But, later you decide to make the game more fun:
let's make the minimal accoutable letters thresshold
configurable for an extra challenge.

You can just do it directly:

```python
def _award_points_for_letters(guessed: int, thresshold: int) -> int:
    return 0 if guessed < thresshold else guessed
```

The problem is that `_award_points_for_letters` is deeply nested.
And then you have to pass `thresshold` through the whole callstack,
including `calculate_points` and all other functions that might be on the way.
All of them will have to accept `thresshold` as a parameter!
This is not useful at all!
Large code bases will struggle a lot from this change.

Ok, you can directly use `django.settings` (or similar)
in your `_award_points_for_letters` function.
And **ruin your pure logic with framework specific details**. That's ugly!

Or you can use `RequiresContext` container. Let's see how our code changes:

```python
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from words_app.logic import calculate_points

def view(request: HttpRequest) -> HttpResponse:
    user_word: str = request.GET['word']  # just an example
    points = calculate_points(user_words)(settings)  # passing the dependencies
    ...  # later you show the result to user somehow

# Somewhere in your `words_app/logic.py`:

from typing_extensions import Protocol
from returns.context import RequiresContext

class _Deps(Protocol):  # we rely on abstractions, not direct values or types
    WORD_THRESSHOLD: int

def calculate_points(word: str) -> RequiresContext[_Deps, int]:
    guessed_letters_count = len([letter for letter in word if letter != '.'])
    return _award_points_for_letters(guessed_letters_count)

def _award_points_for_letters(guessed: int) -> RequiresContext[_Deps, int]:
    return RequiresContext(
        lambda deps: 0 if guessed < deps.WORD_THRESSHOLD else guessed,
    )
```

And now you can pass your dependencies in a really direct and explicit way.
And have the type-safety to check what you pass to cover your back.
Check out [RequiresContext](https://returns.readthedocs.io/en/latest/pages/context.html) docs for more. There you will learn how to make `'.'` also configurable.


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

### Pipe example

```python
import requests
from returns.result import Result, safe
from returns.pipeline import pipe
from returns.pointfree import bind

def fetch_user_profile(user_id: int) -> Result['UserProfile', Exception]:
    """Fetches `UserProfile` TypedDict from foreign API."""
    return pipe(
        _make_request,
        bind(_parse_json),
    )(user_id)

@safe
def _make_request(user_id: int) -> requests.Response:
    # TODO: we are not yet done with this example, read more about `IO`:
    response = requests.get('/api/users/{0}'.format(user_id))
    response.raise_for_status()
    return response

@safe
def _parse_json(response: requests.Response) -> 'UserProfile':
    return response.json()
```

Now we have a clean and a safe and declarative way
to express our business needs:

- We start from making a request, that might fail at any moment,
- Then parsing the response if the request was successful,
- And then return the result.

Now, instead of returning regular values
we return values wrapped inside a special container
thanks to the
[@safe](https://returns.readthedocs.io/en/latest/pages/result.html#safe)
decorator. It will return [Success[YourType] or Failure[Exception]](https://returns.readthedocs.io/en/latest/pages/result.html).
And will never throw exception at us!

We also use [pipe](https://returns.readthedocs.io/en/latest/pages/pipeline.html#pipe)
and [bind](https://returns.readthedocs.io/en/latest/pages/pointfree.html#bind)
functions for handy and declarative composition.

This way we can be sure that our code won't break in
random places due to some implicit exception.
Now we control all parts and are prepared for the explicit errors.

We are not yet done with this example,
let's continue to improve it in the next chapter.


## IO marker

Let's look at our example from another angle.
All its functions look like regular ones:
it is impossible to tell whether they are [pure](https://en.wikipedia.org/wiki/Pure_function)
or impure from the first sight.

It leads to a very important consequence:
*we start to mix pure and impure code together*.
We should not do that!

When these two concepts are mixed
we suffer really bad when testing or reusing it.
Almost everything should be pure by default.
And we should explicitly mark impure parts of the program.

That's why we have created `IO` marker
to mark impure functions that never fail.

These impure functions use `random`, current datetime, environment, or console:

```python
import random
import datetime as dt

from returns.io import IO

def get_random_number() -> IO[int]:  # or use `@impure` decorator
    return IO(random.randint(1, 10))  # isn't pure, because random

now: Callable[[], IO[dt.datetime]] = impure(dt.datetime.now)

@impure
def return_and_show_next_number(previous: int) -> int:
    next_number = previous + 1
    print(next_number)  # isn't pure, because does IO
    return next_number
```

Now we can clearly see which functions are pure and which ones are impure.
This helps us a lot in building large applications, unit testing you code,
and composing bussiness logic together.

### Troublesome IO

As it was already said, we use `IO` when we handle functions that do not fail.

What if our function can fail and is impure?
Like `requests.get()` we had earlier in your example.

Then we have to use `IOResult` instead of a regular `Result`.
Let's find the difference:

- Our `_parse_json` function always return
  the same result (hopefully) for the same input:
  you can either parse valid `json` or fail on invalid one.
  That's why we return pure `Result`
- Our `_make_request` function is impure and can fail.
  Try to send two similar requests with and without internet connection.
  The result will be different for the same input.
  That's why we must use `IOResult` here

So, in order to fulfill our requirement and separate pure code from impure one,
we have to refactor our example.

### Explicit IO

Let's make our [IO](https://returns.readthedocs.io/en/latest/pages/io.html)
explicit!

```python
import requests
from returns.io import IO, IOResult, impure_safe
from returns.result import safe
from returns.pipeline import pipe
from returns.pointfree import bind

def fetch_user_profile(user_id: int) -> IOResult['UserProfile', Exception]:
    """Fetches `UserProfile` TypedDict from foreign API."""
    return pipe(
        _make_request,
        # before: def (Response) -> UserProfile
        # after safe: def (Response) -> ResultE[UserProfile]
        # after bind: def (ResultE[Response]) -> ResultE[UserProfile]
        # after lift: def (IOResultE[Response]) -> IOResultE[UserProfile]
        IOResult.lift_result(bind(_parse_json)),
    )(user_id)

@impure_safe
def _make_request(user_id: int) -> requests.Response:
    response = requests.get('/api/users/{0}'.format(user_id))
    response.raise_for_status()
    return response

@safe
def _parse_json(response: requests.Response) -> 'UserProfile':
    return response.json()
```

And latter we can [unsafe_perform_io](https://returns.readthedocs.io/en/latest/pages/io.html#unsafe-perform-io)
somewhere at the top level of our program to get the pure value.

As a result of this refactoring session, we know everything about our code:

- Which parts can fail,
- Which parts are impure,
- How to compose them in a smart manner.


## More!

Want more? [Go to the docs!](https://returns.readthedocs.io)
Or read these articles:

- [Python exceptions considered an anti-pattern](https://sobolevn.me/2019/02/python-exceptions-considered-an-antipattern)
- [Enforcing Single Responsibility Principle in Python](https://sobolevn.me/2019/03/enforcing-srp)

Do you have an article to submit? Feel free to open a pull request!
