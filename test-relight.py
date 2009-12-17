from __future__ import with_statement

import os
import signal
import subprocess
import sys
import time
import unittest

class TestRelight(unittest.TestCase):

    def setUp(self):
        try:
            os.unlink("relight.log")
        except OSError:
            pass

    def testUsage(self):
        p = subprocess.Popen([sys.executable, "relight.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        self.assertEqual(1, p.returncode)
        output = p.stdout.read()
        self.assertTrue(output.startswith("Usage: "))

    def testBadOption(self):
        p = subprocess.Popen([sys.executable, "relight.py", "-z"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        self.assertEqual(1, p.returncode)
        output = p.stderr.read()
        self.assertEqual("relight: unknown option -z\n", output)

    def testNormal(self):
        p = subprocess.Popen([sys.executable, "relight.py", "sh", "-c", "exit 55"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        self.assertEqual(55, p.returncode)

    def testBasic(self, opts=[]):
        p = subprocess.Popen([sys.executable, "relight.py", "-w", "0"] + opts + ["sh", "-c", "echo $$; sleep 5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.stdout.readline()
        pid = int(output)
        os.kill(pid, signal.SIGKILL)
        err = p.stderr.readline()
        self.assertEqual("relight: process exited with signal %d\n" % signal.SIGKILL, err)
        err = p.stderr.readline()
        self.assertEqual("relight: restarting process now\n", err)

    def testLogfile(self):
        self.testBasic()
        with open("relight.log") as f:
            self.assertTrue("exited with signal %d" % signal.SIGKILL, f.readline())

    def countRelights(self, opts=[]):
        p = subprocess.Popen([sys.executable, "relight.py", "-w", "0"] + opts + ["sh", "-c", "echo $$; sleep 5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        n = 0
        while True:
            output = p.stdout.readline()
            pid = int(output)
            os.kill(pid, signal.SIGKILL)
            err = p.stderr.readline()
            self.assertEqual("relight: process exited with signal %d\n" % signal.SIGKILL, err)
            n += 1
            err = p.stderr.readline()
            if err == "relight: too many restarts, exiting\n":
                p.wait()
                self.assertEqual(1, p.returncode)
                break
            self.assertEqual("relight: restarting process now\n", err)
        return n

    def testNumOption(self):
        self.assertEqual(5, self.countRelights())
        self.assertEqual(3, self.countRelights(["-n", "3"]))

    def testLogfileOption(self):
        try:
            os.unlink("relight2.log")
        except OSError:
            pass
        self.testBasic(["-l", "relight2.log"])
        with open("relight2.log") as f:
            self.assertTrue("exited with signal %d" % signal.SIGKILL, f.readline())

    def measureWait(self, opts=[]):
        p = subprocess.Popen([sys.executable, "relight.py"] + opts + ["sh", "-c", "echo $$; sleep 5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.stdout.readline()
        pid = int(output)
        os.kill(pid, signal.SIGKILL)
        err = p.stderr.readline()
        self.assertEqual("relight: process exited with signal %d\n" % signal.SIGKILL, err)
        start = time.time()
        err = p.stderr.readline()
        self.assertEqual("relight: restarting process now\n", err)
        end = time.time()
        return end - start

    def testWaitOption(self):
        self.assertAlmostEqual(5, self.measureWait(), 2)
        self.assertAlmostEqual(1, self.measureWait(["-w", "1"]), 2)

if __name__ == "__main__":
    unittest.main()
