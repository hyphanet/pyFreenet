#!/usr/bin/env python
# encoding: utf-8

"""

Tests: 

put/get ksk ssk usk dir freesite → data file async

wrong node ip
different IP Port

node methods which need interaction with freenet (not easily doctesteable):

- genkey(self, **kw):
- fcpPluginMessage(self, **kw):
- put(self, uri="CHK@", **kw):
- putdir(self, uri, **kw):
- modifyconfig(self, **kw):
- getconfig(self, **kw):
- invertprivate(self, privatekey):
- redirect(self, srcKey, destKey, **kw):
- genchk(self, **kw):
- listpeers(self, **kw):
- listpeernotes(self, **kw):
- refstats(self, **kw):
- testDDA(self, **kw):
- addpeer(self, **kw):
- listpeer(self, **kw):
- modifypeer(self, **kw):
- modifypeernote(self, **kw):
- removepeer(self, **kw):
- namesiteAddLocal(self, name, privuri=None):
- namesiteAddRecord(self, localname, domain, uri):
- namesiteLookup(self, domain, **kw):
- listenGlobal(self, **kw):
- ignoreGlobal(self, **kw):
- purgePersistentJobs(self):
- getAllJobs(self):
- getPersistentJobs(self):
- getGlobalJobs(self):
- getTransientJobs(self):
- refreshPersistentRequests(self, **kw):
- clearGlobalJob(self, id):
- shutdown(self):


"""

import sys, os, tempfile, random, uuid
import fcp
fcpHost = "127.0.0.1"
workdir = tempfile.mkdtemp()
os.chdir(workdir)

node = fcp.FCPNode(host=fcpHost, verbosity=fcp.DETAIL)

def TEMPLATE():
    '''

    >>> TEMPLATE() 
    None
    '''

