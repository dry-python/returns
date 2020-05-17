.. _pytest-plugins:

pytest plugin
=============

We use special ``pytest`` plugin to improve the testing side of this project.

For example: it is a popular request to ensure
that your container does have its error pass handled.
Because otherwise, developers might forget to do it properly.
It is impossible to fix with types, but is really simple to check with tests.


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

  from returns.result import Failure
  from returns.functions import identity

  def test_my_container(returns):
      assert not returns.is_error_handled(Failure(1))
      assert returns.is_error_handled(Failure(1).fix(identity))

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


Further reading
---------------

- `pytest docs <https://docs.pytest.org/en/latest/contents.html>`_


API Reference
-------------

.. autoclasstree:: returns.contrib.pytest.plugin

.. automodule:: returns.contrib.pytest.plugin
   :members:
