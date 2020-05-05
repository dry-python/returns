Instances
=========

Functions to work with container instances.


is_io
-----

Using ``is_io`` function it's easy to discovery if a instance is IO type
or not, within ``returns`` ecosystem.

.. code:: python

  >>> from returns.instances import is_io
  >>> from returns.io import IOResult
  >>> from returns.result import Success

  >>> success_container = Success('success')
  >>> is_io(success_container)
  False
  >>> is_io(IOResult.from_result(success_container))
  True


is_result
---------

We provide a better way to verify if an instance is Result type or not,
within ``returns`` ecosystem.

.. code:: python

  >>> from returns.instances import is_result
  >>> from returns.maybe import Maybe
  >>> from returns.result import Result

  >>> is_result(Maybe.from_value('maybe'))
  False
  >>> is_result(Result.from_failure('failure'))
  True


API Reference
-------------

.. automodule:: returns.instances
   :members:
