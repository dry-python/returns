Quickstart
==========

Starting is really fast!
You can intergrate ``returns`` into any project at any stage.
You can use it fully or partially. With or without types.

``returns`` is a very flexible library!

You can even just start using it without any deep theory around this project.
But, you can always address our learning materials
which will unravel all parts of functional programming
with useful examples and simple terms.


Why
---

One of the most frequent questions
Python developers ask: why would we need this?

Basically, the answer is that ``returns`` provides
useful abstractions that solve some problems every developer has:

1. :class:`~returns.maybe.Maybe` helps to work with ``None`` in a type-safe way
2. :class:`~returns.result.Result` helps
   to work with exceptions in a type-safe way
3. :class:`~returns.io.IO` helps to separate pure code
   from impure code to make your architecture better
4. :class:`~returns.future.Future` helps to write ``await`` free code
5. :class:`~returns.context.requires_context.RequiresContext` helps
   to inject dependencies in a very readable, explicit, type-safe, and clean way
6. :ref:`pipelines` can be used independently or together with the types above
   to create complex, declarative, and type-safe data pipelines

On top of that we provide useful interfaces that allows you
to switch implementation on the fly.
For example, you can write code that works the same way
for sync and async execution flows.
While being fully type-safe at the same time.

And you can write your own primitives that will solve any other problem
you can possible have based on our existing or your custom interfaces.

In other words, ``returns`` unlocks insane powers
of typed-functional programming to a regular Python developer.


Installation
------------

``returns`` is a pure Python library. Install it as usual:

.. code:: bash

  pip install returns  # or better use poetry


Typechecking and other integrations
-----------------------------------

This step is optional.
If you use ``mypy`` for type-checking, than you will need to configure it.
We really recommend using ``mypy`` with this project though.
Because we have put a lot of efforts into the typing part.

Check out our docs on :ref:`mypy <mypy-plugins>`.

We also have built-in integrations
with :ref:`pytest <pytest-plugins>` and :ref:`hypothesis <hypothesis-plugins>`.
Also, there is :ref:`developer tooling <development-tooling>` you might enjoy.


Theory
------

Do you want to learn new awesome concepts?
Then, start reading our "Userguide"!

It has everything you need! Reading order matters.

However, this is optional.
You can still use ``returns`` without a deep-dive into theory.


Building your own stuff
-----------------------

You can extend ``returns`` and build your own stuff!
Particullary, you can add new interfaces, new containers, and new integrations.
See :ref:`this guide <create-your-own-container>`.

|Telegram chat|

.. |Telegram chat| image:: https://img.shields.io/badge/chat-join-blue?logo=telegram
   :target: https://t.me/drypython

Join our chat to get help or advice.
