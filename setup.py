"""
distutils installation script for pyfcp
"""
import sys, os

doze = sys.platform.lower().startswith("win")

requirements = []
if sys.version_info < (2.5):
    requirements.append("hashlib")

# barf if prerequisite module 'SSLCrypto' is not installed
try:
    if 0:
        sys.stdout.write("Testing if SSLCrypto module is installed...")
        sys.stdout.flush()
        import SSLCrypto
        print "ok!"
except ImportError:
    print "failed!"
    print
    print "You have not installed the SSLCrypto module"
    print "Please refer to the INSTALL file in this directory"
    print "and follow the instructions"
    print
    print "You can continue with this installation, but you will"
    print "not have the protection of encrypted config files."
    resp = raw_input("Continue installation anyway? [Y/n] ")
    resp = resp.strip().lower() or "y"
    resp = resp[0]
    if resp == 'n':
        print "Installation aborted"
        sys.exit(1)
    else:
        print "Installing without encryption"

# barf if user is not running this script as root
#if not doze:
#    if (os.getuid() != 0):
#        print "You must be root to do this installation"
#        sys.exit(1)

scripts = ["freesitemgr", "pyNodeConfig", 
           "fcpget", "fcpput", "fcpupload", "fcpgenkey", "fcpinvertkey", "fcpredirect", "fcpnames", 
           "fproxyproxy"# , "freedisk"  # <- not yet reviewed
           ]
if doze:
    for i in range(len(scripts)):
        scripts[i] += ".py"

from distutils.core import setup
setup(name="PyFCP",
      version="0.1.2",
      description="Freenet FCP access freesite management and XML-RPC modules",
      author="David McNab",
      author_email="david@freenet.org.nz",
       url ="http://127.0.0.1:8888/USK@T4gW1EvwSrR9AOlBT2hFnWy5wK0rtd5rGhf6bp75tVo,E9uFCy0NhiTbR0jVQkY77doaWtxTrkS9kuMrzOtNzSQ,AQABAAE/pyfcp/0",

      packages = ['fcp'],
      py_modules = [], # ["minibot"], # <- not yet reviewed
      scripts = scripts,
      requires = requirements,
    )


if not doze:
    os.system("cp manpages/*.1 /usr/share/man/man1")

