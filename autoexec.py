#@+leo
#@+node:0::@file autoexec.py
#@+body
# You can ignore this file - it's just used for testing.
# If you set the env var PYTHONSTARTOP=autoexec.py, then
# running python will automatically execute this file.

#import freenet_
#print dir(freenet_)
#from freenet_ import *

#print "importing freenet"

from pdb import set_trace

#set_trace()

from freenet import *

#verbosity(4)

#connect("hermes")

#print "connected to FCP @ hermes"
#a = access()
#print "got access object 'a'"

#x = a.getKey("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet", raw=0)
#x = a.getKey("KSK@gpl.txt")
#m = x.metadata

#m = metadata()
#print "adding file1"
#m.add("file1", "Redirect", target="blah")
#print "adding file2"
#m.add("file2/file3", "Redirect", target="CHK@blah", mimetype="mimetype1")
#print "adding file3"
#m.add("file3/foo", "DateRedirect", target="KSK@haha", increment=3600)
#print "adding file4"
#m.add("file4", "SplitFile", splitsize=65536, splitchunks=['CHK@chunk1', 'CHK@chunk2'])

#print "Created empty metadata object 'm'"

#print "starting key insert"
#a.openKey("555", "w", htl=1)
#a.writeKey("Hi, this is KSK@555\n")
#a.closeKey()

#set_trace()
#print 'hello'
#def doit():
#	global mm
#	f = open('testmeta')
#	s = f.read()
#	f.close()
#	mm= metadata(s)
	#print "Revision = '%s'" % mm.metaRevision
	#print "Parts = ", mm.metaParts
	#print "Trailing = ", mm.metaTrailing

#ff = site(name="mysite",
#			  fromdir="/main/freesites/testsite",
#			  htl=0)
#print "Created freesite object 'ff'"
#ff.insert()

#lst = ff.readdir("/tmp/blah")
#for f in lst.keys():
#	print f, lst[f]

#doit()

#verbosity(2, 4)

#set_trace()
#a = key.put("KSK@123", "This is ksk@123", htl=0)

#fs = site.insert("/main/freesites/testsite", htl=0)

#k = key.get("CHK@eN0Em4wJUu7zeLlYm2w7kzEW3y8KAwI,kzjcBfGXhJvpseL7vS6RvA", raw=1)

#mysite = site.get("SSK@ADKF8pkxs3PnIdz-WruV~rmMmKMPAgM/site//", "/tmp/freesite")


#mysite = site.get("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet//",
#				  "/main/freesites/others/pyfreenet")

#site.get("SSK@fgbuxwSCCjOJHsUI-9-uijD1haQPAgM/flinks/8//",
#		 "/main/freesites/others/flinks",
#		 htl=1)


#site.get("SSK@h~ixmz11-tDOox9O1gQyjkzAUCcPAgM/fmb/5//",
#		 "/main/freesites/others/fmb",
#		 htl=12)

#f = fcp("hermes")

#set_trace()
#dat, met = f.getKey("KSK@aa")

#import freenet
#freenet.host = "hermes"

#freenet.verbosity(4)

#m = metadata()
#m.add('')
#m.set('', 'Info.Artist', 'Jimi Hendrix')

#set_trace()
#x = fcp.put("Purple Haze", m, None, 0)

#s = site.get("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet//", "/tmp/pyf")

#set_trace()
connect("hermes")

#x = fproxyGet("KSK@aa")
#y = fproxyGet("SSK@rdRr~qa898tOpfh4QPDV6mMY0jgPAgM/pyFreenet//pyFreenet-0.1.tar.gz")


# freenet:CHK@GAe2NrIQsqLU9-wSdSrlImsgE2wLAwI,HNstQ496ceRzRuqhIbHksw
#k = fish.putfile("CHK@", "ian1.jpg", 0)

#set_trace()
#res = gj.getFecFile("CHK@GAe2NrIQsqLU9-wSdSrlImsgE2wLAwI,HNstQ496ceRzRuqhIbHksw",
#					"ian1-req.jpg", "hermes", 8481, 25)

#set_trace()
#k = fcp.get("CHK@GAe2NrIQsqLU9-wSdSrlImsgE2wLAwI,HNstQ496ceRzRuqhIbHksw")
#fd = open("/tmp/pic.jpg", "wb")
#fd.write(str(k))
#fd.close()

import testsuite
#testsuite.run()
testsuite.test01()
testsuite.test02()
testsuite.test10()
testsuite.test11()

#@-body
#@-node:0::@file autoexec.py
#@-leo
