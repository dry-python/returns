.. _mypy-plugins:

mypy plugin
===========

We provide a custom ``mypy`` plugin to fix existing issues,
provide new awesome features,
and improve type-safety of things developers commonly use.


Installation
------------

You will need to install ``mypy`` separately.
It is not bundled with ``returns``.

To install any ``mypy`` plugin add it
to the ``plugins`` section of the config file (``setup.cfg`` or ``mypy.ini``):

.. code:: ini

  [mypy]
  plugins =
    returns.contrib.mypy.returns_plugin

Or in ``pyproject.toml``:

.. code:: toml

  [tool.mypy]
  plugins = ["returns.contrib.mypy.returns_plugin"]

We recommend to always add our plugin as the first one in chain.


Configuration
-------------

You can have a look at the suggested ``mypy``
`configuration <https://github.com/dry-python/returns/blob/master/setup.cfg>`_
in our own repository.

You can also use `nitpick <https://wemake-python-stylegui.de/en/latest/pages/usage/integrations/nitpick.html>`_
tool to enforce the same ``mypy`` configuration for all your projects.

We recommend to use our own setup. Add this to your ``pyproject.toml``:

.. code:: toml

  [tool.nitpick]
  style = "https://raw.githubusercontent.com/wemake-services/wemake-python-styleguide/master/styles/mypy.toml"

And use ``flake8`` to lint that configuration
defined in the setup matches yours.
This will allow to keep them in sync with the upstream.


Supported features
------------------

- ``kind`` feature adds Higher Kinded Types (HKT) support
- ``curry`` feature allows to write typed curried functions
- ``partial`` feature allows to write typed partial application
- ``flow`` feature allows to write better typed functional pipelines
  with ``flow`` function
- ``pipe`` feature allows to write better typed functional pipelines
  with ``pipe`` function
- ``do-notation`` feature allows using :ref:`do-notation`


Further reading
---------------

- `Mypy official docs <https://mypy.readthedocs.io/en/stable/index.html>`_
- `Mypy plugins docs <https://mypy.readthedocs.io/en/stable/extending_mypy.html>`_


API Reference
-------------

Plugin definition
~~~~~~~~~~~~~~~~~

.. automodule:: returns.contrib.mypy._consts
   :members:

.. autoclasstree:: returns.contrib.mypy.returns_plugin
   :strict:

.. automodule:: returns.contrib.mypy.returns_plugin
   :members:

Kind
~~~~

.. autoclasstree:: returns.contrib.mypy._features.kind
   :strict:

.. automodule:: returns.contrib.mypy._features.kind
   :members:

Curry
~~~~~

.. autoclasstree:: returns.contrib.mypy._features.curry
   :strict:

.. automodule:: returns.contrib.mypy._features.curry
   :members:

Partial
~~~~~~~

.. autoclasstree:: returns.contrib.mypy._features.partial
   :strict:

.. automodule:: returns.contrib.mypy._features.partial
   :members:

Flow
~~~~

.. autoclasstree:: returns.contrib.mypy._features.flow
   :strict:

.. automodule:: returns.contrib.mypy._features.flow
   :members:

Pipe
~~~~

.. autoclasstree:: returns.contrib.mypy._features.pipe
   :strict:

.. automodule:: returns.contrib.mypy._features.pipe
   :members:

Do notation
~~~~~~~~~~~

.. autoclasstree:: returns.contrib.mypy._features.do_notation
   :strict:

.. automodule:: returns.contrib.mypy._features.do_notation
   :members:
