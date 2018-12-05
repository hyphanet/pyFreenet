README file for pyFreenet3

<<<<<<< variant A
**Currently outdated**: Not yet reviewed changes can be found in 
<https://github.com/ArneBab/lib-pyFreenet-staging/tree/py3>.

fcpVersion = "0.3.4"


PyFreenet is a suite of command-line freenet applications, as well as a
>>>>>>> variant B
PyFreenet3 is a suite of command-line freenet applications, as well as a
####### Ancestor
fcpVersion = "0.3.4"


PyFreenet is a suite of command-line freenet applications, as well as a
======= end
powerful Python library, for Freenet.


Install via 

    $ pip3 install --upgrade --user pyFreenet3


To just upload a file into Freenet (currently only on GNU/Linux), install a Java JRE or JDK and then use

    $ fcpupload --spawn <file>

It starts a Freenet node, uploads the file and returns the key to access the file via Freenet.


If you need a library for Python 2, please use pyFreenet.


This pyFreenet3 release includes:

 - command-line freenet client applications, which will get installed as
   executable commands in your PATH, including:

     - freesitemgr - a simple yet flexible freesite management utility
     - fcpnames - utility for managing the new 'name service' layer
     - fproxyproxy - an experimental http proxy that sits on top of
       fproxy, and translates human-friendly site names transparently
     - fcpget - a single key fetcher
     - fcpput - a single key inserter
     - fcpgenkey - a keypair generator
     - fcpinvertkey - generate new SSK/USK keypairs
     - fcpredirect - insert a redirect from one 'key' to another 'key'.
     - copyweb - download a page from a website with all resources.

 - python package 'fcp', containing classes for interacting with freenet.

 - an XML-RPC server for freenet access, which can be run standalone, or
   easily integrated into an existing website

To get good API documentation, run:

    $ epydoc -n "pyFreenet API manual" -o html fcp

When you install this package (refer INSTALL), you should 
end up with a command 'freesitemgr' on your PATH.

'freesitemgr' is a console-based freesite insertion utility
which keeps your freesite configs and status in a single
config file (~/.freesitemgr, unless you specify otherwise).

Just use 'freesitemgr add FOLDER' to upload a website into Freenet.

Invoke 'freesitemgr -h' (or if on windows, 'freesitemgr.py -h')
and read the options.

