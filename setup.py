"""
distutils installation script for pyfcp
"""
import sys

if sys.platform.lower().startswith("win"):
    freesitemgrScript = "freesitemgr.py"
    fcpgetScript = "fcpget.py"
    fcpputScript = "fcpput.py"
else:
    freesitemgrScript = "freesitemgr"
    fcpgetScript = "fcpget"
    fcpputScript = "fcpput"

from distutils.core import setup
setup(name="PyFCP",
      version="0.1",
      description="Freenet FCP access freesite management and XML-RPC modules",
      author="David McNab",
      author_email="david@freenet.org.nz",
       url ="http://127.0.0.1:8888/USK@yhAqcwNdN1y1eyRQQwZfhu4dpn-tPNlZMeNRZxEg1bM,zBUodpjtZdJvzWmwYKgr8jO5V-yKxZvetsr8tADNg2U,AQABAAE/pyfcp/0",

      packages = ['fcp'],
      scripts = [freesitemgrScript, fcpgetScript, fcpputScript],


#      py_modules=["fcp", "fcpxmlrpc", "fcpsitemgr"]

    )

