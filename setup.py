"""
distutils installation script for pyfcp
"""
import sys, os

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
if (os.getuid() != 0) and not sys.platform.lower().startswith("win"):
    print "You must be root to do this installation"
    sys.exit(1)


if sys.platform.lower().startswith("win"):
    freesitemgrScript = "freesitemgr.py"
    fcpgetScript = "fcpget.py"
    fcpputScript = "fcpput.py"
    fcpgenkeyScript = "fcpgenkey.py"
    fcpinvertScript = "fcpinvertkey.py"
    freediskScript = "freedisk.py"
else:
    freesitemgrScript = "freesitemgr"
    fcpgetScript = "fcpget"
    fcpputScript = "fcpput"
    fcpgenkeyScript = "fcpgenkey"
    fcpinvertScript = "fcpinvertkey"
    freediskScript = "freedisk"

from distutils.core import setup
setup(name="PyFCP",
      version="0.1",
      description="Freenet FCP access freesite management and XML-RPC modules",
      author="David McNab",
      author_email="david@freenet.org.nz",
       url ="http://127.0.0.1:8888/USK@yhAqcwNdN1y1eyRQQwZfhu4dpn-tPNlZMeNRZxEg1bM,zBUodpjtZdJvzWmwYKgr8jO5V-yKxZvetsr8tADNg2U,AQABAAE/pyfcp/0",

      packages = ['fcp'],
      scripts = [freesitemgrScript, fcpgetScript, fcpputScript,
                 fcpgenkeyScript, fcpinvertScript,
                 freediskScript,
                 ],


#      py_modules=["fcp", "fcpxmlrpc", "fcpsitemgr"]

    )

