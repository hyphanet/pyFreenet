#@+leo
#@+node:0::@file Makefile
#@+body
#
# Makefile for building Python module for Freenet FCP access
#
# Written by David McNab, released under the GNU Lesser General
# Public License, no warrantee - yada yada yada

all: docs

clean:
	rm -rf *.pyc *~ build html dist

docs:
	PYFREENETDOC=1 epydoc freenet.py
	rm -rf doc/classref
	mv html doc/classref

install:
	python setup.py install

install-doc:
	mkdir -p /usr/share/doc/pyFreenet
	cp -rp doc/* /usr/share/doc/pyFreenet


#@-body
#@-node:0::@file Makefile
#@-leo
