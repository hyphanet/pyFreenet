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
      version="0.2.0",
      description="Freenet Client Protocol Helper",
      author="Arne Babenhauserheide",
      author_email="arne_bab@web.de",
      url="http://127.0.0.1:8888/USK@9X7bw5HD2ufYvJuL3qAVsYZb3KbI9~FyRu68zsw5HVg,lhHkYYluqHi7BcW1UHoVAMcRX7E5FaZjWCOruTspwQQ,AQACAAE/pyfcp-api/0/",
      packages = ['fcp'],
      py_modules = [], # ["minibot"], # <- not yet reviewed
      scripts = scripts,
      requires = requirements,
    )


# TODO: Only do this when the installation is to /
#       currently man-page install is broken with --user
# some pointers which did not work:
# import distutils.command.install
# import distutils.dist
# i = distutils.command.install.install(distutils.dist.Distribution())
# i.finalize_options()
# i.finalize_unix()
# print i.convert_paths("data")
# print i.root, i.prefix
if not doze:
    os.system("cp manpages/*.1 /usr/share/man/man1")

