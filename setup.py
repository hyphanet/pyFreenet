#!/usr/bin/env python
#@+leo-ver=4
#@+node:@file setup.py
#@@first #!/usr/bin/env python
#@@language python

# This file does the python-specific build and install
# for pyFreenet
#
# Written David McNab, 11 Feb 2003

import sys,os
from distutils.core import setup, Extension

setup(name='freenet',
	  version = '0.2.4',
	  description = 'pyFreenet - Python API for Freenet access',
	  py_modules = ['freenet']
	  )

#@-node:@file setup.py
#@-leo
