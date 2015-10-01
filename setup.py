"""
distutils installation script for pyFreenet
"""
import sys
import os
import logging
import distutils.command.install
from distutils.core import setup



doze = sys.platform.lower().startswith("win")

scripts = ["freesitemgr", "pyNodeConfig", 
           "fcpget", "fcpput", "fcpupload", "fcpgenkey", "fcpinvertkey", "fcpredirect", "fcpnames", 
           "fproxyproxy", "copyweb"  # , "freedisk"  # <- not yet reviewed
           ]
if doze:
    for i in range(len(scripts)):
        scripts[i] += ".py"


class pyfreenet_install(distutils.command.install.install):
    def run(self, *args, **kwds):
        distutils.command.install.install.run(self, *args, **kwds)
        man_dir = os.path.abspath("./manpages/")
        man_target_dir = os.path.join(self.install_base, "share/man/man1")
        try:
            print "Creating man-page directory at", man_target_dir
            os.makedirs(man_target_dir)
        except Exception as e:
            if str(e).endswith("File exists: '" + man_target_dir + "'"):
                print "info: Could not create man-page directory: already existed."
            else:
                print e
        if not doze:
            os.system("cp " + man_dir + "/*.1 " + man_target_dir)


setup(name="pyFreenet",
      version="0.3.2",
      description="Freenet Client Protocol Helper",
      author="Arne Babenhauserheide",
      author_email="arne_bab@web.de",
      url="http://127.0.0.1:8888/USK@38~ZdMc3Kgjq16te1A7UvRrAZadwviLgePY~CzCq32c,Z9vOKndIpemk~hfwg5yQvZKetfrm6AXs36WKVCvIOBo,AQACAAE/pyFreenet/1/",
      packages = ['fcp'],
      scripts = scripts,
      cmdclass={"install": pyfreenet_install} # thanks to lc-tools
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

