#!/usr/bin/env python
#@+leo
#@+node:0::@file testsuite.py
#@+body
#@@first
#@@language python
#@+others
#@+node:1::declarations
#@+body
"""
testsuite.py
Runs a series of tests of pyFreenet package.
"""

import freenet


# set these to your freenet node's address

#freenet_fcp_host = "127.0.0.1"
#freenet_fcp_host = "192.168.2.1"
freenet_fcp_host = "192.168.1.3"

#freenet_fcp_port = 8481
freenet_fcp_port = 8482
randomshit = "some stuff which gets endlessly repeated in a key 123"
randomsize = 1400000

import sys, time, os
from pdb import set_trace


#@-body
#@-node:1::declarations
#@+node:2::test01()
#@+body
def test01():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 01: import the module"
	import freenet
	freenet.verbosity(4)
	print "TESTSUITE: PASSED\n\n"



#@-body
#@-node:2::test01()
#@+node:3::test02()
#@+body
def test02():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 02: connect to node"
	try:
		freenet.connect(freenet_fcp_host, freenet_fcp_port)
	except:
		print "TESTSUITE: failed"
		raise
	print "TESTSUITE: PASSED\n\n"



#@-body
#@-node:3::test02()
#@+node:4::test03()
#@+body
def test03():
	global keyname
	global myuri
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 03: Create a basic URI"
	keyname = "KSK@pyFreenetTest%s" % time.strftime("%H%M%S")
	myuri = freenet.uri(keyname)
	print "TESTSUITE: PASSED - key = '%s'" % str(myuri)


#@-body
#@-node:4::test03()
#@+node:5::test04()
#@+body

def test04():
	global keyname
	global myuri
	global insertedksk
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 04: Insert a basic KSK key - raw"
	try:
		print "TESTSUITE: Inserting as URI: '%s'" % myuri
		insertedksk = freenet.node.put("This is key '%s'\n" % keyname, '', myuri, htl=0)
	except:
		print "TESTSUITE: failed"
		raise
	print "TESTSUITE: uri = '%s'" % insertedksk.uri
	print "TESTSUITE: PASSED\n\n" % insertedksk.uri


#@-body
#@-node:5::test04()
#@+node:6::test05()
#@+body

def test05():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 05: Retrieve the key back again"
	print "TESTSUITE: (any big delay here is probably a bug)"

	global insertedksk

	try:
		k = freenet.node.get(insertedksk.uri)
	except:
		print "TESTSUITE: failed"
		raise
	print "TESTSUITE: Key uri = %s" % k.uri
	print "TESTSUITE: Key data:\n", k
	print "TESTSUITE: PASSED\n\n"


#@-body
#@-node:6::test05()
#@+node:7::test06()
#@+body

def test06():
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 06: Insert a key with metadata, and retrieve"
	try:
		m = freenet.metadata()
		m.add('', mimetype="text/html")
		txt = "<html><head><title>pyFreenet test 06</title></head><body><h1>test 06</h1>This is test 06 - seems ok</body></html>\n"
		uri = freenet.uri("KSK@test06-%s" % time.strftime("%H%M%S"))
		k = freenet.node.put(txt, m, uri, htl=0)
		kr = freenet.node.get(uri)
		print "TESTSUITE: retrieved URI = ", kr.uri
		print "TESTSUITE: retrieved text:\n", kr
		print "TESTSUITE: with metadata:\n", kr.metadata
	except:
		#print failed
		raise
	print "TESTSUITE: PASSED\n\n"



#@-body
#@-node:7::test06()
#@+node:8::test07()
#@+body

def test07():
	global pubkey
	global privkey
	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 07: generate an SSK keypair"
	pubkey, privkey = freenet.node.genkeypair()
	print "TESTSUITE: pubkey='%s', privkey='%s'" % (pubkey, privkey)
	print "TESTSUITE: PASSED"


#@-body
#@-node:8::test07()
#@+node:9::test08()
#@+body

def test08():
    global pubkey
    global privkey
    global siteuri
    global mydir

    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: test 08: Create and insert a dummy freesite"
    print
    mydir = "testsite-%s" % time.strftime("%H%M%S")
    print "TESTSUITE: (creating freesite in directory '%s')" % mydir
    os.mkdir(mydir)
    fd = open(mydir+"/index.html", "w")
    fd.write('<html><head><title>my testsite</title></head>\n')
    fd.write('<body>\n')
    fd.write('<h1>TestSite</h1>\n')
    fd.write('File: <a href="subdir/file.txt">subdir/file.txt</a>\n')
    fd.write('</body></html>\n')
    fd.close()
    os.mkdir(mydir+"/subdir")
    fd = open(mydir+"/subdir/file.txt", "w")
    fd.write("This is file.txt from the test freesite")
    fd.close()
    print "TESTSUITE: Freesite created at %s" % mydir
    print "TESTSUITE: Inserting freesite..."
    siteuri = freenet.site.put(mydir, name="testsite", pub=pubkey, priv=privkey, htl=0)
    print "TESTSUITE: Site URI = %s" % siteuri
    print "TESTSUITE: PASSED\n\n"


#@-body
#@-node:9::test08()
#@+node:10::test09()
#@+body

def test09():
	global siteuri, mydir

	print "TESTSUITE: ********************************************************"
	print "TESTSUITE: test 09: Retrieve this site back"
	print
	print "TESTSUITE: Retrieving site '%s'" % siteuri

	mysite = freenet.site.get(siteuri, mydir + "-get")
	print "TESTSUITE: site retrieved successfully"
	print "TESTSUITE: Retrieved URI = ", mysite.uri
	print "TESTSUITE: deleting site directories"
	os.system("rm -rf testsite-*")
	print "TESTSUITE: PASSED\n\n"


#@-body
#@-node:10::test09()
#@+node:11::test10()
#@+body

def test10():
    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: test 10: Generate and Insert a large file."
    print
    # Change the string below to create a unique file.
    # The purpose of creating the same file each time is so that you don't flood
    # your datastore with crap each time you run these tests.
    print "TESTSUITE: Note - edit this test script if you want to insert new random rubbish."
    print

    global biginsertedkey
    global fileOrig
    global fileCheck

    print "TESTSUITE: Creating large file..."
    fileOrig = freenet.tempFilename()
    fileCheck = freenet.tempFilename()
    fd = open(fileOrig, "wb")
    size = 0
    linenum = 1
    while size < randomsize:
        nextline = "%s: line %d\n" % (randomshit, linenum)
        linenum += 1
        fd.write(nextline)
        size += len(nextline)
    fd.close()
    print "TESTSUITE: Done."

    # change this later to use fcp.putfile()
    print "TESTSUITE: Reading large file into memory..."
    fd = open(fileOrig)
    rawdata = fd.read()
    fd.close()
    print "TESTSUITE: Done."
    print "TESTSUITE: Inserting this large file - this might take ages..."

    #set_trace()

    #biginsertedkey = freenet.node.put(rawdata, None, None, 0)
    mynode = freenet.node(freenet_fcp_host, freenet_fcp_port)
    biginsertedkey = mynode.put(rawdata, None, None, 0, allowSplitfiles=0)
    print "TESTSUITE: Big file '%s' apparently inserted fine" % fileOrig
    print "TESTSUITE: Inserted URI: %s" % biginsertedkey.uri
    print "TESTSUITE: PASSED\n\n"

#@-body
#@-node:11::test10()
#@+node:12::test11()
#@+body

def test11():
    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: test 11: Get big file inserted in test10, and compare"
    print

    global biginsertedkey
    global fileOrig
    global fileCheck

    try:
        rxuri = biginsertedkey.uri
        print "TESTSUITE: Aiming to retrieve URI: %s" % rxuri
        print "TESTSUITE: This might take a while..."
        bigretrievedkey = freenet.node.get(rxuri)
        print "TESTSUITE: Seems to have retrieved OK - now compare!"
        insdata = str(biginsertedkey)
        retdata = str(bigretrievedkey)
        if insdata != retdata:
            print "TESTSUITE: Difference in files: orig size %d, retrieved size %d" % \
                  len(insdata), len(retdata)
            raise Exception("what we retrieved is not what we inserted!")
        else:
            print "TESTSUITE: Inserted file and retrieved file are identical"
            print "TESTSUITE: PASSED\n\n"
            
    except:
        print "TESTSUITE: **************************"
        print "TESTSUITE:  TEST 11 FAILED!!!! :((("
        print "TESTSUITE: **************************"
        raise


#@-body
#@-node:12::test11()
#@+node:13::run()
#@+body

def run():
    test01()
    test02()
    test03()
    test04()
    test05()
    test06()
    test07()
    test08()
    test09()
    test10()
    test11()

    print
    print "TESTSUITE: ********************************************************"
    print "TESTSUITE: All tests succeeded - module 'freenet' awaits you"
    print "TESTSUITE: ********************************************************"
    print



#@-body
#@-node:13::run()
#@+node:14::mainline()
#@+body
if __name__ == '__main__':
    run()

#@-body
#@-node:14::mainline()
#@-others


# Automated test suite for pyFreenet.

# If your pyFreenet installation was successfuly, you should 
# try running this script, which will put pyFreenet through
# 11 tests.


#@-body
#@-node:0::@file testsuite.py
#@-leo
