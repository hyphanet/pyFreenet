"""
distutils installation script for pyFreenet
"""
import sys, os

doze = sys.platform.lower().startswith("win")

scripts = ["freesitemgr", "pyNodeConfig", 
           "fcpget", "fcpput", "fcpupload", "fcpgenkey", "fcpinvertkey", "fcpredirect", "fcpnames", 
           "fproxyproxy", "loadplugin"# , "freedisk"  # <- not yet reviewed
           ]
if doze:
    for i in range(len(scripts)):
        scripts[i] += ".py"

from distutils.core import setup
setup(name="pyFreenet",
      version="0.2.5",
      description="Freenet Client Protocol Helper",
      author="Arne Babenhauserheide",
      author_email="arne_bab@web.de",
      url="http://127.0.0.1:8888/USK@38~ZdMc3Kgjq16te1A7UvRrAZadwviLgePY~CzCq32c,Z9vOKndIpemk~hfwg5yQvZKetfrm6AXs36WKVCvIOBo,AQACAAE/pyFreenet/1/",
      packages = ['fcp'],
      scripts = scripts,
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

