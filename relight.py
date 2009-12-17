#!/usr/bin/env python

# relight.py - restart errant processes
# Greg Hewgill <greg@hewgill.com> http://hewgill.com
#
# LICENSE
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the author be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# Copyright (c) 2009 Greg Hewgill

import os
import sys
import time

RELIGHTS = 5
LOGFILE = "relight.log"
WAIT = 5

a = 1
while a < len(sys.argv) and sys.argv[a].startswith("-"):
    if sys.argv[a] == "-n":
        a += 1
        RELIGHTS = int(sys.argv[a])
        a += 1
    elif sys.argv[a] == "-l":
        a += 1
        LOGFILE = sys.argv[a]
        a += 1
    elif sys.argv[a] == "-w":
        a += 1
        WAIT = int(sys.argv[a])
        a += 1
    else:
        print >>sys.stderr, "relight: unknown option", sys.argv[a]
        sys.exit(1)

if a >= len(sys.argv):
    print "Usage: %s [options] command args ..." % sys.argv[0]
    print
    print "        -n restarts"
    print "            number of restarts within a minute before we give up (default 5)"
    print "        -l logfile"
    print "            name of log file (default relight.log)"
    print "        -w wait"
    print "            seconds to wait between restarts (default 5)"
    sys.exit(1)

current_minute = int(time.time() / 60)
restarts = 0

while True:
    pid = os.fork()
    if pid == 0:
        os.execlp(sys.argv[a], *sys.argv[a:])

    #print >>sys.stderr, "relight: pid", pid
    pid, status = os.waitpid(pid, 0)
    exitcode = (status >> 8) & 0xff
    signal = status & 0xff
    if signal == 0:
        sys.exit(exitcode)

    print >>sys.stderr, "relight: process exited with signal", signal
    log = open(LOGFILE, "a")
    print >>log, time.ctime(), "exited with signal", signal
    log.close()

    minute = int(time.time() / 60)
    if minute != current_minute:
        current_minute = minute
        restarts = 0
    restarts += 1
    if restarts >= RELIGHTS:
        print >>sys.stderr, "relight: too many restarts, exiting"
        sys.exit(1)

    time.sleep(WAIT)
    print >>sys.stderr, "relight: restarting process now"
