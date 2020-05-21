.. _mypy-plugins:

mypy plugin
===========

We provide several ``mypy`` plugins to fix existing issues
and improve type-safety of things developers commonly use:

- ``returns_plugin`` to solve untyped `decorator issue <https://github.com/python/mypy/issues/3157>`_ and add better :ref:`curry` support


Installation
------------

To install any ``mypy`` plugin add it
to the ``plugins`` section of the config file.

.. code:: ini

  [mypy]
  plugins =
    returns.contrib.mypy.returns_plugin

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

- ``curry`` feature allows to write typed curried functions
- ``partial`` feature allows to write typed partial application
- ``flow`` feature allows to write better typed functional pipelines
- ``decorators`` allows to infer types of functions that are decorated
  with ``@safe``, ``@maybe``, ``@impure``, etc
- ``pointfree`` provides better typing inference
  for some problematic :ref:`pointfree` helpers


Further reading
---------------

- `Mypy official docs <https://mypy.readthedocs.io/en/stable/index.html>`_
- `Mypy plugins docs <https://mypy.readthedocs.io/en/stable/extending_mypy.html>`_


API Reference
-------------

Plugin defenition
~~~~~~~~~~~~~~~~~

.. autoclasstree:: returns.contrib.mypy.returns_plugin

.. automodule:: returns.contrib.mypy.returns_plugin
   :members:

Curry
~~~~~

.. autoclasstree:: returns.contrib.mypy._features.curry

.. automodule:: returns.contrib.mypy._features.curry
   :members:

Partial
~~~~~~~

.. autoclasstree:: returns.contrib.mypy._features.partial

.. automodule:: returns.contrib.mypy._features.partial
   :members:

Flow
~~~~

.. autoclasstree:: returns.contrib.mypy._features.flow

.. automodule:: returns.contrib.mypy._features.flow
   :members:

Decorators
~~~~~~~~~~

.. autoclasstree:: returns.contrib.mypy._features.decorators

.. automodule:: returns.contrib.mypy._features.decorators
   :members:


Pointfree
~~~~~~~~~

.. autoclasstree:: returns.contrib.mypy._features.pointfree

.. automodule:: returns.contrib.mypy._features.pointfree
   :members:
