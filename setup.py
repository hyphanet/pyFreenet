"""
distutils installation script for pyfcp
"""
import sys, os

doze = sys.platform.lower().startswith("win")

# barf if prerequisite module 'SSLCrypto' is not installed
try:
    sys.stdout.write("Testing if SSLCrypto module is installed...")
    sys.stdout.flush()
    import SSLCrypto
    print "ok!"
except:
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
if not doze:
    if (os.getuid() != 0):
        print "You must be root to do this installation"
        sys.exit(1)

if doze:
    freesitemgrScript = "freesitemgr.py"
    fcpgetScript = "fcpget.py"
    fcpputScript = "fcpput.py"
    fcpgenkeyScript = "fcpgenkey.py"
    fcpinvertScript = "fcpinvertkey.py"
    fcpredirectScript = "fcpredirect.py"
    freediskScript = "freedisk.py"
    fcpnamesScript = "fcpnames.py"
else:
    freesitemgrScript = "freesitemgr"
    fcpgetScript = "fcpget"
    fcpputScript = "fcpput"
    fcpgenkeyScript = "fcpgenkey"
    fcpinvertScript = "fcpinvertkey"
    fcpredirectScript = "fcpredirect"
    freediskScript = "freedisk"
    fcpnamesScript = "fcpnames"

from distutils.core import setup
setup(name="PyFCP",
      version="0.1",
      description="Freenet FCP access freesite management and XML-RPC modules",
      author="David McNab",
      author_email="david@freenet.org.nz",
       url ="http://127.0.0.1:8888/USK@T4gW1EvwSrR9AOlBT2hFnWy5wK0rtd5rGhf6bp75tVo,E9uFCy0NhiTbR0jVQkY77doaWtxTrkS9kuMrzOtNzSQ,AQABAAE/pyfcp/0",

      packages = ['fcp'],
      scripts = [freesitemgrScript, fcpgetScript, fcpputScript,
                 fcpgenkeyScript, fcpinvertScript, fcpredirectScript,
                 freediskScript, fcpnamesScript,
                 ],


#      py_modules=["fcp", "fcpxmlrpc", "fcpsitemgr"]

    )


if not doze:
    os.system("cp manpages/*.1 /usr/share/man/man1")

