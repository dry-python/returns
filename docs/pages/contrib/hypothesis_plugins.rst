.. _hypothesis-plugins:

hypothesis plugin
=================

We provide several extra features for Hypothesis users.
And encourage to use it together with ``returns``.


Installation
------------

You will need to install ``hypothesis`` separately.
It is not bundled with ``returns``.

We also require ``anyio`` package for this plugin to work with async laws.


hypothesis entrypoint
---------------------

We support a ``hypothesis`` entrypoint
that is executed on ``hypothesis`` import.

There we are regestering all our containers as strategies.
So, you don't have to. Example:

.. code:: python

  from returns.result import Result
  from hypothesis import strategies as st

  assert st.from_type(Result).example()

This is a convenience thing only.


strategy_from_container
-----------------------

We provide a utility function
to create ``hypothesis`` strategy from any container.

You can use it to easily register your own containers.

.. code:: python

  from hypothesis import strategies as st
  from returns.contrib.hypothesis.containers import strategy_from_container

  st.register_type_strategy(
      YourContainerClass,
      strategy_from_container(YourContainerClass),
  )

You can also pass ``use_init`` keyword argument
if you wish to use ``__init__`` method to instantiate your containers.
Turned off by default.
Example:

.. code:: python

  st.register_type_strategy(
      YourContainerClass,
      strategy_from_container(YourContainerClass, use_init=True),
  )

Or you can write your own ``hypothesis`` strategy. It is also fine.


check_all_laws
--------------

We also provide a very powerful mechanism of checking defined container laws.
It works in a combitation with "Laws as Values" feature we provide in the core.

.. code:: python

  from returns.contrib.hypothesis.laws import check_all_laws
  from your.module import YourCustomContainer

  check_all_laws(YourCustomContainer)

This one line of code will generate ~100 tests for all defined law
in both ``YourCustomContainer`` and all its super types,
including our internal ones.

We also provide a way to configure
the checking process with ``settings_kwargs``:

.. code:: python

  check_all_laws(YourCustomContainer, settings_kwargs={'max_examples': 500})

This will increase the number of generated test to 500.
We support all kwargs from ``@settings``, see
`@settings docs <https://hypothesis.readthedocs.io/en/latest/settings.html>`_.

You can also change how ``hypothesis`` creates instances of your container.
By default, we use ``.from_value``, ``.from_optional``, and ``.from_failure``
if we are able to find them.

But, you can also pass types without these methods,
but with ``__init__`` defined:

.. code:: python

  from typing import Callable, TypeVar
  from typing_extensions import final
  from returns.interfaces.mappable import Mappable1
  from returns.primitives.container import BaseContainer
  from returns.primitives.hkt import SupportsKind1

  _ValueType = TypeVar('_ValueType')
  _NewValueType = TypeVar('_NewValueType')

  @final
  class Number(
      BaseContainer,
      SupportsKind1['Number', _ValueType],
      Mappable1[_ValueType],
  ):
      def __init__(self, inner_value: _ValueType) -> None:
          super().__init__(inner_value)

      def map(
          self,
          function: Callable[[_ValueType], _NewValueType],
      ) -> 'Number[_NewValueType]':
          return Number(function(self._inner_value))

  # We want to allow ``__init__`` method to be used:
  check_all_laws(Number, use_init=True)

As you see, we don't support any ``from`` methods here.
But, ``__init__`` would be used to generate values thanks to ``use_init=True``.

By default, we don't allow to use ``__init__``,
because there are different complex types
like ``Future``, ``ReaderFutureResult``, etc
that have complex ``__init__`` signatures.
And we don't want to mess with them.

Warning::
  Checking laws is not compatible with ``pytest-xdist``,
  because we use a lot of global mutable state there.
  Please, use ``returns_lawful`` marker
  to exclude them from ``pytest-xdist`` execution plan.


Further reading
---------------

- `Projects Extending hypothesis <https://hypothesis.readthedocs.io/en/latest/strategies.html>`_


API Reference
-------------

Types we have already registered for you
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: returns.contrib.hypothesis._entrypoint
   :members:

DSL to register custom containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: returns.contrib.hypothesis.containers
   :members:

DSL to define laws
~~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.primitives.laws
   :strict:

.. automodule:: returns.primitives.laws
   :members:

Plugin internals
~~~~~~~~~~~~~~~~

.. automodule:: returns.contrib.hypothesis.laws
   :members:
