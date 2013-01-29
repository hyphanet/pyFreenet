#!/usr/bin/env python
# encoding: utf-8

"""

Tests: 

put/get ksk ssk usk dir freesite → data file async

wrong node ip
different IP Port
"""

import sys, os, tempfile, random, uuid
import fcp
fcpHost = "127.0.0.1"
workdir = tempfile.mkdtemp()
os.chdir(workdir)

node = fcp.FCPNode(host=fcpHost, verbosity=fcp.FATAL)

def genkey(*args, **kwds):
    '''

    >>> public, private = genkey()
    >>> fcp.node.uriIsPrivate(public)
    False
    >>> fcp.node.uriIsPrivate(private)
    True
    '''
    return node.genkey(*args, **kwds)

def getUniqueId(*args, **kwds):
    '''

    >>> getUniqueId().startswith("id")
    True
    '''
    return node._getUniqueId(*args, **kwds)

def submitCmd(*args, **kwds):
    '''

    >>> connid = getUniqueId()
    >>> job = submitCmd(connid, "GetNode", async=True, Identifier=connid)
    >>> job.wait()["Identifier"] == connid
    True
    >>> submitCmd(connid, "GetNode", Identifier=connid)["Identifier"] == connid
    True
    >>> raw = """GetNode
    ... WithPrivate=true
    ... WithVolatile=false
    ... Identifier=""" + connid + """
    ... EndMessage
    ... """
    >>> submitCmd(connid, "GetNode", rawcmd=raw)["Identifier"] == connid
    True
    
    '''
    return node._submitCmd(*args, **kwds)


def fcpPluginMessage(*args, **kwds):
    '''

    >>> fcpPluginMessage(id="pyfreenet",
    ...     plugin_name="plugins.HelloFCP.HelloFCP") 
    [{'header': 'FCPPluginReply', 'PluginName': 'plugins.HelloFCP.HelloFCP', 'Identifier': 'pyfreenet'}]
    
    '''
    return node.fcpPluginMessage(*args, **kwds)

def put(*args, **kwds):
    '''

    >>> # put() 
    
    '''
    return node.put(*args, **kwds)

def putdir(*args, **kwds):
    '''

    >>> # putdir() 
    
    '''
    return node.putdir(*args, **kwds)

def modifyconfig(*args, **kwds):
    '''

    >>> # modifyconfig() 
    
    '''
    return node.modifyconfig(*args, **kwds)

def getconfig(*args, **kwds):
    '''

    >>> # getconfig() 
    
    '''
    return node.getconfig(*args, **kwds)

def invertprivate(*args, **kwds):
    '''

    >>> # invertprivate() 
    
    '''
    return node.invertprivate(*args, **kwds)

def redirect(*args, **kwds):
    '''

    >>> # redirect() 
    
    '''
    return node.redirect(*args, **kwds)

def genchk(*args, **kwds):
    '''

    >>> # genchk() 
    
    '''
    return node.genchk(*args, **kwds)

def listpeers(*args, **kwds):
    '''

    >>> # listpeers() 
    
    '''
    return node.listpeers(*args, **kwds)

def listpeernotes(*args, **kwds):
    '''

    >>> # listpeernotes() 
    
    '''
    return node.listpeernotes(*args, **kwds)

def refstats(*args, **kwds):
    '''

    >>> # refstats() 
    
    '''
    return node.refstats(*args, **kwds)

def testDDA(*args, **kwds):
    '''

    >>> # testDDA() 
    
    '''
    return node.testDDA(*args, **kwds)

def addpeer(*args, **kwds):
    '''

    >>> # addpeer() 
    
    '''
    return node.addpeer(*args, **kwds)

def listpeer(*args, **kwds):
    '''

    >>> # listpeer() 
    
    '''
    return node.listpeer(*args, **kwds)

def modifypeer(*args, **kwds):
    '''

    >>> # modifypeer() 
    
    '''
    return node.modifypeer(*args, **kwds)

def modifypeernote(*args, **kwds):
    '''

    >>> # modifypeernote() 
    
    '''
    return node.modifypeernote(*args, **kwds)

def removepeer(*args, **kwds):
    '''

    >>> # removepeer() 
    
    '''
    return node.removepeer(*args, **kwds)

def namesiteAddLocal(*args, **kwds):
    '''

    >>> # namesiteAddLocal() 
    
    '''
    return node.namesiteAddLocal(*args, **kwds)

def namesiteAddRecord(*args, **kwds):
    '''

    >>> # namesiteAddRecord() 
    
    '''
    return node.namesiteAddRecord(*args, **kwds)

def namesiteLookup(*args, **kwds):
    '''

    >>> # namesiteLookup() 
    
    '''
    return node.namesiteLookup(*args, **kwds)

def listenGlobal(*args, **kwds):
    '''

    >>> # listenGlobal() 
    
    '''
    return node.listenGlobal(*args, **kwds)

def ignoreGlobal(*args, **kwds):
    '''

    >>> # ignoreGlobal() 
    
    '''
    return node.ignoreGlobal(*args, **kwds)

def purgePersistentJobs(*args, **kwds):
    '''

    >>> # purgePersistentJobs() 
    
    '''
    return node.purgePersistentJobs(*args, **kwds)

def getAllJobs(*args, **kwds):
    '''

    >>> # getAllJobs() 
    
    '''
    return node.getAllJobs(*args, **kwds)

def getPersistentJobs(*args, **kwds):
    '''

    >>> # getPersistentJobs() 
    
    '''
    return node.getPersistentJobs(*args, **kwds)

def getGlobalJobs(*args, **kwds):
    '''

    >>> # getGlobalJobs() 
    
    '''
    return node.getGlobalJobs(*args, **kwds)

def getTransientJobs(*args, **kwds):
    '''

    >>> # getTransientJobs() 
    
    '''
    return node.getTransientJobs(*args, **kwds)

def refreshPersistentRequests(*args, **kwds):
    '''

    >>> # refreshPersistentRequests() 
    
    '''
    return node.refreshPersistentRequests(*args, **kwds)

def clearGlobalJob(*args, **kwds):
    '''

    >>> # clearGlobalJob() 
    
    '''
    return node.clearGlobalJob(*args, **kwds)

def shutdown(*args, **kwds):
    '''

    >>> # shutdown() 
    
    '''
    return node.shutdown(*args, **kwds)


def _base30hex(integer):
    """Turn an integer into a simple lowercase base30hex encoding."""
    base30 = "0123456789abcdefghijklmnopqrst"
    b30 = []
    while integer:
        b30.append(base30[integer%30])
        integer = int(integer / 30)
    return "".join(reversed(b30))
        

def _test():
    import doctest
    tests = doctest.testmod()
    if tests.failed:
        return "☹"*tests.failed
    return "^_^ (" + _base30hex(tests.attempted) + ")"
        

if __name__ == "__main__":
    print _test()
