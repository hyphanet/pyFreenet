"""
passlib setup script

This script honors one environmental variable:
PASSLIB_SETUP_TAG_RELEASE
    if "yes" (the default), revision tag is appended to version.
    for release, this is explicitly set to "no".
"""
#=============================================================================
# init script env -- ensure cwd = root of source dir
#=============================================================================
import os
root_dir = os.path.abspath(os.path.join(__file__, ".."))
os.chdir(root_dir)

#=============================================================================
# imports
#=============================================================================
import re
from setuptools import setup, find_packages
import subprocess
import sys
import time
PY3 = (sys.version_info[0] >= 3)

#=============================================================================
# init setup options
#=============================================================================
opts = {"cmdclass": {}}
args = sys.argv[1:]

#=============================================================================
# register docdist command (not required)
#=============================================================================
try:
    from freenet_passlib_170._setup.docdist import docdist
    opts['cmdclass']['docdist'] = docdist
except ImportError:
    pass

#=============================================================================
# version string / datestamps
#=============================================================================

# pull version string from freenet_passlib_170
from freenet_passlib_170 import __version__ as version

# by default, stamp HG revision to end of version
if os.environ.get("PASSLIB_SETUP_TAG_RELEASE", "y").lower() in "yes y true t 1".split():
    # call HG via subprocess
    # NOTE: for py26 compat, using Popen() instead of check_output()
    try:
        proc = subprocess.Popen(["hg", "tip", "--template", "{date(date, '%Y%m%d%H%M%S')}+hg.{node|short}"],
                                stdout=subprocess.PIPE)
        stamp, _ = proc.communicate()
        if proc.returncode:
            raise subprocess.CalledProcessError(1, [])
        stamp = stamp.decode("ascii")
    except (OSError, subprocess.CalledProcessError):
        # fallback - just use build date
        stamp = time.strftime("%Y%m%d%H%M%S")

    # modify version
    if version.endswith((".dev0", ".post0")):
        version = version[:-1] + stamp
    else:
        version += ".post" + stamp

    # subclass build_py & sdist so they rewrite passlib/__init__.py
    # to have the correct version string
    from freenet_passlib_170._setup.stamp import stamp_distutils_output
    stamp_distutils_output(opts, version)

#=============================================================================
# static text
#=============================================================================
SUMMARY = "comprehensive password hashing framework supporting over 30 schemes"

DESCRIPTION = """\
Passlib is a password hashing library for Python 2 & 3, which provides
cross-platform implementations of over 30 password hashing algorithms, as well
as a framework for managing existing password hashes. It's designed to be useful
for a wide range of tasks, from verifying a hash found in /etc/shadow, to
providing full-strength password hashing for multi-user applications.

* See the `documentation <https://freenet_passlib_170.readthedocs.io>`_
  for details, installation instructions, and examples.

* See the `homepage <https://bitbucket.org/ecollins/passlib>`_
  for the latest news and more information.

* See the `changelog <https://freenet_passlib_170.readthedocs.io/en/stable/history>`_
  for a description of what's new in Passlib.

All releases are signed with the gpg key
`4D8592DF4CE1ED31 <http://pgp.mit.edu:11371/pks/lookup?op=get&search=0x4D8592DF4CE1ED31>`_.
"""

KEYWORDS = """\
password secret hash security
crypt md5-crypt
sha256-crypt sha512-crypt pbkdf2 argon2 scrypt bcrypt
apache htpasswd htdigest
totp 2fa
"""

CLASSIFIERS = """\
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: Jython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Security :: Cryptography
Topic :: Software Development :: Libraries
""".splitlines()

# TODO: "Programming Language :: Python :: Implementation :: IronPython" -- issue 34

is_release = False
if '.dev' in version:
    CLASSIFIERS.append("Development Status :: 3 - Alpha")
elif '.post' in version:
    CLASSIFIERS.append("Development Status :: 4 - Beta")
else:
    is_release = True
    CLASSIFIERS.append("Development Status :: 5 - Production/Stable")

#=============================================================================
# run setup
#=============================================================================
# XXX: could omit 'freenet_passlib_170._setup' from eggs, but not sdist
setup(
    # package info
    packages=find_packages(root_dir),
    package_data={
        "freenet_passlib_170.tests": ["*.cfg"],
        "passlib": ["_data/wordsets/*.txt"],
    },
    zip_safe=True,

    # metadata
    name="passlib",
    version=version,
    author="Eli Collins",
    author_email="elic@assurancetechnologies.com",
    license="BSD",

    url="https://bitbucket.org/ecollins/passlib",
    download_url=
        ("https://pypi.python.org/packages/source/p/passlib/passlib-" + version + ".tar.gz")
        if is_release else None,

    description=SUMMARY,
    long_description=DESCRIPTION,
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,

    tests_require='nose >= 1.1',
    test_suite='nose.collector',

    extras_require={
        "argon2": "argon2_cffi>=16.2",
        "bcrypt": "bcrypt>=3.1.0",
        "totp": "cryptography",
    },

    # extra opts
    script_args=args,
    **opts
)

#=============================================================================
# eof
#=============================================================================
