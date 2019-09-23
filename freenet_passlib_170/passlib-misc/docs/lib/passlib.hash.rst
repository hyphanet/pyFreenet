==============================================
:mod:`passlib.hash` - Password Hashing Schemes
==============================================

.. module:: passlib.hash
    :synopsis: all password hashes provided by Passlib

Overview
========
The :mod:`!passlib.hash` module contains all the password hash algorithms built into Passlib.
While each hash has its own options and output format,
they all inherit from the :mod:`~passlib.ifc.PasswordHash` base interface.
The following pages describe each hash in detail,
including its format, underlying algorithm, and known security issues.

.. rst-class:: float-center

.. danger::

    **Many of the hash algorithms listed below are *NOT* secure.**

    Passlib supports a wide array of hash algorithms, primarily to
    support dealing with legacy data and systems.

    If you're looking to choose a hash algorithm for a new application,
    see the :doc:`Quickstart Guide </narr/quickstart>` instead of picking
    one from this list.

.. rst-class:: float-center

.. seealso::

    :ref:`hash-tutorial` -- for general usage examples

.. _mcf-hashes:

Unix Hashes
===========
Aside from "archaic" schemes such as :class:`!des_crypt`,
most of the password hashes supported by modern Unix flavors
adhere to the :ref:`modular crypt format <modular-crypt-format>`,
allowing them to be easily distinguished when used within the same file.
The basic of format :samp:`${scheme}${hash}` has also been adopted for use
by other applications and password hash schemes.

.. _standard-unix-hashes:

.. rst-class:: toc-always-open

Active Unix Hashes
------------------
All these schemes are actively in use by various Unix flavors to store user passwords.
They all follow the modular crypt format.

.. toctree::
    :maxdepth: 1

    passlib.hash.bcrypt
    passlib.hash.sha256_crypt
    passlib.hash.sha512_crypt

Special note should be made of the following fallback helper,
which is not an actual hash scheme, but implements the "disabled account marker"
found in many Linux & BSD password files:

.. toctree::
    :maxdepth: 1

    passlib.hash.unix_disabled

.. rst-class:: toc-always-open

Deprecated Unix Hashes
----------------------
The following schemes are supported by various Unix systems
use the modular crypt format, and are noticably stronger than the previous group.
However, they have all since been deprecated in favor of stronger algorithms:

* :class:`passlib.hash.bsd_nthash` - FreeBSD's MCF-compatible encoding of :doc:`nthash <passlib.hash.nthash>` digests

.. toctree::
    :maxdepth: 1

    passlib.hash.md5_crypt
    passlib.hash.sha1_crypt
    passlib.hash.sun_md5_crypt

.. _archaic-unix-schemes:

.. rst-class:: toc-always-open

Archaic Unix Hashes
-------------------
The following schemes are supported by certain Unix systems,
but are considered particularly archaic: Not only do they predate
the modular crypt format, but they're based on the outmoded DES block cipher,
and are woefully insecure:

.. toctree::
    :maxdepth: 1

    passlib.hash.des_crypt
    passlib.hash.bsdi_crypt
    passlib.hash.bigcrypt
    passlib.hash.crypt16

Other "Modular Crypt" Hashes
============================
The :ref:`modular crypt format <modular-crypt-format>` is a loose standard
for password hash strings which started life under the Unix operating system,
and is used by many of the Unix hashes (above).  However, it's
it's basic :samp:`${scheme}${hash}` format has also been adopted by a number
of application-specific hash algorithms:

.. rst-class:: toc-always-open

Active Hashes
-------------
While most of these schemes generally require an application-specific
implementation, natively used by any Unix flavor to store user passwords,
they can be used compatibly along side other modular crypt format hashes:

.. toctree::
    :maxdepth: 1

    passlib.hash.argon2
    passlib.hash.bcrypt_sha256
    passlib.hash.phpass
    passlib.hash.pbkdf2_digest
    passlib.hash.scram
    passlib.hash.scrypt

.. rst-class:: toc-always-open

Deprecated Hashes
-----------------
The following are some additional application-specific hashes which are still
occasionally seen, use the modular crypt format, but are rarely used or weak
enough that they have been deprecated:

.. toctree::
    :maxdepth: 1

    passlib.hash.apr_md5_crypt
    passlib.hash.cta_pbkdf2_sha1
    passlib.hash.dlitz_pbkdf2_sha1

.. _ldap-hashes:

LDAP / RFC2307 Hashes
=====================

All of the following hashes use a variant of the password hash format
used by LDAPv2. Originally specified in :rfc:`2307` and used by OpenLDAP [#openldap]_,
the basic format ``{SCHEME}HASH`` has seen widespread adoption in a number of programs.

.. _standard-ldap-hashes:

Standard LDAP Schemes
---------------------
.. toctree::
    :hidden:

    passlib.hash.ldap_std

The following schemes are explicitly defined by RFC 2307,
and are supported by OpenLDAP.

* :class:`passlib.hash.ldap_md5` - MD5 digest
* :class:`passlib.hash.ldap_sha1` - SHA1 digest
* :class:`passlib.hash.ldap_salted_md5` - salted MD5 digest
* :class:`passlib.hash.ldap_salted_sha1` - salted SHA1 digest

.. toctree::
    :maxdepth: 1

    passlib.hash.ldap_crypt

* :class:`passlib.hash.ldap_plaintext` - LDAP-Aware Plaintext Handler

Non-Standard LDAP Schemes
-------------------------
None of the following schemes are actually used by LDAP,
but follow the LDAP format:

.. toctree::
    :hidden:

    passlib.hash.ldap_other

* :class:`passlib.hash.ldap_hex_md5` - Hex-encoded MD5 Digest
* :class:`passlib.hash.ldap_hex_sha1` - Hex-encoded SHA1 Digest

.. toctree::
    :maxdepth: 1

    passlib.hash.ldap_pbkdf2_digest
    passlib.hash.atlassian_pbkdf2_sha1
    passlib.hash.fshp

* :class:`passlib.hash.roundup_plaintext` - Roundup-specific LDAP Plaintext Handler

.. _database-hashes:

SQL Database Hashes
===================
The following schemes are used by various SQL databases
to encode their own user accounts.
These schemes have encoding and contextual requirements
not seen outside those specific contexts:

.. toctree::
    :maxdepth: 1

    passlib.hash.mssql2000
    passlib.hash.mssql2005
    passlib.hash.mysql323
    passlib.hash.mysql41
    passlib.hash.postgres_md5
    passlib.hash.oracle10
    passlib.hash.oracle11

.. _windows-hashes:

MS Windows Hashes
=================
The following hashes are used in various places by Microsoft Windows.
As they were designed for "internal" use, they generally contain
no identifying markers, identifying them is pretty much context-dependant.

.. toctree::
    :maxdepth: 1

    passlib.hash.lmhash
    passlib.hash.nthash
    passlib.hash.msdcc
    passlib.hash.msdcc2

.. rst-class:: toc-always-toggle

Cisco Hashes
============
The following hashes are used in various places on Cisco IOS and ASA devices:

.. toctree::
    :maxdepth: 1

    passlib.hash.cisco_pix
    passlib.hash.cisco_asa

* **Cisco "Type 5" hashes** - these are the same as :doc:`md5_crypt <passlib.hash.md5_crypt>`

.. toctree::
    :maxdepth: 1

    passlib.hash.cisco_type7

.. _other-hashes:

Other Hashes
============
The following schemes are used in various contexts,
but have formats or uses which cannot be easily placed
in one of the above categories:

.. toctree::
    :maxdepth: 1

    passlib.hash.django_std
    passlib.hash.grub_pbkdf2_sha512
    passlib.hash.hex_digests
    passlib.hash.plaintext

.. rubric:: Footnotes

.. [#openldap] OpenLDAP homepage - `<http://www.openldap.org/>`_.


