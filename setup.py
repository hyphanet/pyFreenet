"""
distutils installation script for pyFreenet
"""
import sys
import os
import logging
import distutils.command.install
from distutils.core import setup



doze = sys.platform.lower().startswith("win")

if sys.version_info.major <= 2:
    scripts = [] # avoid installing scripts from py2
else:
    scripts = ["freesitemgr", "pyNodeConfig",
               "fcpget", "fcpput", "fcpupload", "fcpgenkey", "fcpinvertkey", "fcpredirect", "fcpnames",
               "fproxyproxy", "copyweb", "babcom_cli"  # , "freedisk"  # <- not yet reviewed
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
            print("Creating man-page directory at", man_target_dir)
            os.makedirs(man_target_dir)
        except Exception as e:
            if str(e).endswith("File exists: '" + man_target_dir + "'"):
                print("info: Could not create man-page directory: already existed.")
            else:
                print(e)
        if not doze:
            os.system("cp " + man_dir + "/*.1 " + man_target_dir)


setup(name="pyFreenet3",
      version="0.4.9",
      description="Freenet Client Protocol Helper",
      author="Arne Babenhauserheide",
      author_email="arne_bab@web.de",
      url="http://127.0.0.1:8888/USK@~osOPnNLdMLVrYVNTahLufdwOuMhhC4GkpIHulnSm04,bwAmjkK-BZZnj-bujBQehwgGqUM1AUFhzTW4hcDGXQ0,AQACAAE/infocalypse_and_pyFreenet/5/",
      packages = ['fcp3', 'freenet3', 'freenet_passlib_170'] + [
          'freenet_passlib_170' + "." + i
          for i in "crypto ext ext.django handlers passlib-misc _setup".split() +
          "utils utils.compat crypto._blowfish crypto.scrypt".split()],
      scripts = scripts,
      cmdclass={"install": pyfreenet_install}, # thanks to lc-tools
      classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      long_description = open("README").read()
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

