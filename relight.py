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
