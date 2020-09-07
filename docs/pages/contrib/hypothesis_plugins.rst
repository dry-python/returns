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

Warning::
  This module does not support ``python3.6``,
  please upgrade to at least ``python3.7``!


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

.. automodule:: returns.contrib.hypothesis.laws
   :members:
