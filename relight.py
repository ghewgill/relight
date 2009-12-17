#!/usr/bin/env python

import os
import sys
import time

current_minute = int(time.time() / 60)
restarts = 0

while True:
    pid = os.fork()
    if pid == 0:
        os.execlp(sys.argv[1], *sys.argv[1:])

    #print >>sys.stderr, "relight: pid", pid
    pid, status = os.waitpid(pid, 0)
    exitcode = (status >> 8) & 0xff
    signal = status & 0xff
    if signal == 0:
        sys.exit(exitcode)

    print >>sys.stderr, "relight: process exited with signal", signal
    log = open("relight.log", "a")
    print >>log, time.ctime(), "exited with signal", signal
    log.close()

    minute = int(time.time() / 60)
    if minute != current_minute:
        current_minute = minute
        restarts = 0
    restarts += 1
    if restarts >= 5:
        print >>sys.stderr, "relight: too many restarts, exiting"
        sys.exit(1)

    time.sleep(5)
    print >>sys.stderr, "relight: restarting process now"
