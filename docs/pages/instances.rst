Instances
=========

Functions to work with container instances.


is_io
-----

Using ``is_io`` function it's easy to discovery if a instance is IO type
or not within ``returns`` ecosystem.

.. code:: python

  >>> from returns.instances import is_io
  >>> from returns.io import IOResult
  >>> from returns.result import Success

  >>> success_container = Success('success')
  >>> is_io(success_container)
  False
  >>> is_io(IOResult.from_result(success_container))
  True


API Reference
-------------

.. automodule:: returns.instances
   :members:
