#!/usr/bin/env python3

"""Test for the purge-db4o breakage when using WatchGlobal."""

import fcp
import time
n = fcp.node.FCPNode()
n.verbosity = 6
n._submitCmd(id=None, cmd='WatchGlobal', **{'Enabled': 'true'})
while n.nodeIsAlive:
    time.sleep(1)
