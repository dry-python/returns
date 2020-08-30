.. _pytest-plugins:

pytest plugin
=============

We use special ``pytest`` plugin to improve the testing side of this project.

For example: it is a popular request to ensure
that your container does have its error pass handled.
Because otherwise, developers might forget to do it properly.
It is impossible to fix with types, but is really simple to check with tests.


Installation
------------

You will need to install ``pytest`` separately.


Usage
-----

There's no need to install anything special.
``pytest`` will automatically find and use this plugin.

To use it in your tests, request ``returns`` fixture like so:

.. code:: python

  def test_my_container(returns):
      ...

is_error_handled
~~~~~~~~~~~~~~~~

The first helper we define is ``is_error_handled`` function.
It tests that containers do handle error track.

.. code:: python

  from returns.result import Failure, Success

  def test_my_container(returns):
      assert not returns.is_error_handled(Failure(1))
      assert returns.is_error_handled(
          Failure(1).rescue(lambda _: Success('default value')),
      )

We recommed to unit test big chunks of code this way.
This is helpful for big pipelines where
you need at least one error handling at the very end.

This is how it works internally:

- Methods like ``fix`` and ``rescue`` mark errors
  inside the container as handled
- Methods like ``map`` and ``alt`` just copies
  the error handling state from the old container to a new one,
  so there's no need to re-handle the error after these methods
- Methods like ``bind`` create new containers with unhandled errors

.. note::

  We use monkeypathing of containers inside tests to make this check possible.
  They are still purely functional inside.
  It does not affect production code.


has_trace
~~~~~~~~~

Sometimes we have to know if a container is created correctly in a specific
point of our flow.

``has_trace`` helps us to check exactly this by identifying when a container is
created and looking for the desired function.

.. code:: python

  >>> from returns.result import Result, Success, Failure

  >>> returns_fixture = getfixture('returns')

  >>> def desired_function(arg: str) -> Result[int, str]:
  ...     if arg.isnumeric():
  ...         return Success(int(arg))
  ...     return Failure('"{0}" is not a number'.format(arg))

  >>> def test_if_failure_is_created_at_convert_function(returns):
  ...     with returns.has_trace(Failure, desired_function):
  ...         Success('not a number').bind(desired_function)

  >>> def test_if_success_is_created_at_convert_function(returns):
  ...     with returns.has_trace(Success, desired_function):
  ...         Success('42').bind(desired_function)

  >>> test_if_failure_is_created_at_convert_function(returns_fixture)
  >>> test_if_success_is_created_at_convert_function(returns_fixture)


Further reading
---------------

- `pytest docs <https://docs.pytest.org/en/latest/contents.html>`_


API Reference
-------------

.. autoclasstree:: returns.contrib.pytest.plugin

.. automodule:: returns.contrib.pytest.plugin
   :members:
