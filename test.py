#!/usr/bin/env python2
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
myid = str(uuid.uuid4().hex)
with open("index.html", "w") as f:
    f.write("<html><head><title>Test</title></head><body>Test</body></html>\n")

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
    
    - uri=ksk ssk usk × data file dir redirect
    - dontcompress, chkonly, mimetype, waituntilsent, async
    - persistence, Verbosity, priority, realtime, Global
    - timeout (for the insertion)

    >>> data = "23"
    >>> kwds = {"async": True, "realtime": True, "priority": 1, "waituntilsent": True}
    >>> public, private = genkey()
    >>> privateusk = "U" + private[1:] + "test/0/data"
    >>> publicusk = "U" + public[1:] + "test/0/data"
    >>> chkput = put(data=data, **kwds)
    >>> uskput = put(uri=privateusk, data=data, **kwds)
    >>> sskput = put(uri=private + "test", data=data, **kwds)
    >>> kskput = put(uri="KSK@"+myid, data=data, **kwds)
    >>> redirput = put(uri="KSK@redirectto"+myid, redirect="KSK@"+myid, **kwds)
    >>> dirput = put(dir=workdir, **kwds)
    >>> # the following wait until freenet is really finished 
    >>> # so they are horribly slow. Activate them manually.
    >>> # chkput.wait()
    >>> True # uskput.wait() == publicusk
    True
    >>> True # sskput.wait() == public + "test"
    True
    >>> # kskput.wait()
    >>> # redirput.wait()
    >>> # dirput.wait()
    
    '''
    return node.put(*args, **kwds)

def get(uri, *args, **kwds):
    '''
    
    >>> # warning: this can be slow the first time you run it.
    >>> mime, data = get("KSK@gpl.txt", realtime=True, priority=0)[:2]
    >>> data[:9]
    '\\t\\t    GNU'
    >>> # rest tested in put
    
    '''
    return node.get(uri, *args, **kwds)

f
def putdir(*args, **kwds):
    '''
    
    putdir is a specialization of dir. It’s tested with put.

    - name, usk (for dir-mode)
    
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

    >>> data = "test"
    >>> chk = genchk(data=data)
    >>> chkres = put(data=data, priority=0, realtime=True)
    >>> chk == chkres
    True
    >>> got = get(uri=chk, priority=0, realtime=True)
    >>> gotmime, gotdata, gotdict = got
    >>> gotdata == gotdict["Data"]
    True
    >>> gotdata == data
    True
    >>> foomime = "bla/foo"
    >>> # chkfoo = genchk(data=data, mimetype=foomime)
    >>> # got2 = get(uri=chkfoo, priority=0, realtime=True)
    >>> True # got2[1] == data
    True
    >>> True # got2[0] == foomime
    True
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
        return "☹"*tests.failed + " / " + str(tests.attempted)
    return "^_^ (" + _base30hex(tests.attempted) + ")"
        

if __name__ == "__main__":
    print _test()
