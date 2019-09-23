.. module:: passlib.pwd
    :synopsis: password generation helpers

=================================================
:mod:`passlib.pwd` -- Password generation helpers
=================================================

.. versionadded:: 1.7

Password Generation
===================

.. rst-class:: float-center

.. warning::

    Before using these routines, make sure your system's RNG entropy pool is
    secure and full. Also make sure that :func:`!genword` or :func:`!genphrase`
    is called with a sufficiently high ``entropy`` parameter
    the intended purpose of the password.

.. autofunction:: genword(entropy=None, length=None, charset="ascii_62", chars=None, returns=None)

.. autofunction:: genphrase(entropy=None, length=None, wordset="eff_long", words=None, sep=" ", returns=None)

Predefined Symbol Sets
======================
The following predefined sets are used by the generation functions above,
but are exported by this module for general use:

.. object:: default_charsets

    Dictionary mapping charset name -> string of characters, used by :func:`genword`.
    See that function for a list of predefined charsets present in this dict.

.. object:: default_wordsets

    Dictionary mapping wordset name -> tuple of words, used by :func:`genphrase`.
    See that function for a list of predefined wordsets present in this dict.

    (Note that this is actually a special object which will lazy-load
    wordsets from disk on-demand)

Password Strength Estimation
============================
Passlib does not current offer any password strength estimation routines.
However, the (javascript-based) `zxcvbn <https://github.com/dropbox/zxcvbn>`_
project is a very good choice. There are a few python ports of ZCVBN library, though as of 2016-11,
none of them seem active and up to date.

The following is a list of known ZCVBN python ports, though it's not clear which of these
is active and/or official:

* https://github.com/dropbox/python-zxcvbn -- seemingly official python version,
  but not updated since 2013, and not published on pypi.

* https://github.com/rpearl/python-zxcvbn -- fork of official version,
  also not updated since 2013, but released to pypi as `"zxcvbn" <https://pypi.python.org/pypi/zxcvbn>`_.

* https://github.com/gordon86/python-zxcvbn -- fork that has some updates as of july 2015,
  released to pypi as `"zxcvbn-py3" <https://pypi.python.org/pypi/zxcvbn-py3>`_ (and compatible
  with 2 & 3, despite the name).
