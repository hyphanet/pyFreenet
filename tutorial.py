#!/usr/bin/env python2

import sys, os, tempfile, random, uuid

# ------------------------------------------
# This is a tutorial introduction to
# pyFreenet, arranged as comments and code
# interspersed in a python script
# 
# read through this carefully, and learn
# ------------------------------------------


# ------------------------------------------
# first things first - import fcp module

import fcp

# ------------------------------------------
# state where our FCP port is

fcpHost = "127.0.0.1"


# ------------------------------------------
# create a node connection object
# 
# we're setting a relatively high verbosity so you
# can see the traffic

node = fcp.FCPNode(host=fcpHost, verbosity=fcp.DETAIL)


# -----------------------------------------------
# now, perform a simple direct insert of a string

# val = raw_input("Please enter a string to insert: ")
# ksk = raw_input("Please enter a short KSK key name: ")
val = "testinsert"
ksk = "testinsertkey" + uuid.uuid4().hex

uri = "KSK@" + ksk
print "Inserting %s, containing '%s'" % (uri, val)

# do the put - note that 'data=' inserts a string directly
# note too that mimetype is optional, defaulting to text/plain
node.put("KSK@"+ksk, data=val, mimetype="text/plain")

print "insert completed successfully"

# ------------------------------------------
# now, retrieve it back

print "trying to retrieve our value back"
mimetype, val1, msg = node.get(uri)

# ensure it's correct
if val == val1:
    print "retrieved ok, values match"
else:
    print "huh? values don't match"

# ------------------------------------------
# now, insert from a file

# val = raw_input("Please enter a string to insert: ")
# ksk = raw_input("Please enter a short KSK key name: ")
# path = raw_input("Enter a temporary filename: ")
val = "testinsertforfile"
ksk = "testkeyforfile"  + uuid.uuid4().hex
tmpdir = tempfile.mkdtemp()
path = os.path.join(tmpdir, "testinsertfile")

# write our string to a file
f = file(path, "w")
f.write(val)
f.close()

uri = "KSK@" + ksk
print "Inserting %s, from file '%s'" % (uri, path)

# do the put - note that 'file=' inserts from a filename or file object
node.put("KSK@"+ksk, file=path)

# ------------------------------------------
# now, demonstrate asynchronous requests

print "Launching asynchronous request"
job = node.get(uri, async=True)

# we can poll the job
if job.isComplete():
    print "Yay! job complete"
else:
    # or we can await its completion
    result = job.wait()

print "Result='%s'" % str(result)

# ------------------------------------------
# similarly, we can get to a file

# path = raw_input("temporary file to retrieve to: ")
path = os.path.join(tmpdir, "testgetfile")
node.get(uri, file=path)

# again, the 'file=' can be a pathname or an open file object

# ------------------------------------------
# TODO: demonstrate persistent requests

# ------------------------------------------
# TODO: demonstrate global requests

