#!/bin/bash

# a wrapper which starts the freenet node,
# and is used with the cron'ed freesite insertion
# scripts

# change this to where your bash startup script lives
source /home/david/.bashrc

# change this to where your freenet is installed
cd /home/david/freenet

# now start the freenet node
./run.sh start

