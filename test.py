#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 13 11:13:48 2017

@author: john
"""

# Reference: https://gist.github.com/sloria/7001839

import loom
import multiprocessing
import queue
import time
import unittest

class LoomTest(unittest.TestCase):
    
    def test_initialization_with_args(self):
        l = loom.loom(10)
        self.assertEqual(l._poolsize, 10, "Pool size was not set correctly at initialization")
        self.assertEqual(str(l._pool)[0:36], '<multiprocessing.pool.Pool object at', "Pool was not created at initialization")

    def test_initialization_without_args(self):
        l = loom.loom()
        self.assertEqual(l._poolsize, multiprocessing.cpu_count(), "Pool size was not set correctly at initialization")
        self.assertEqual(str(l._pool)[0:36], '<multiprocessing.pool.Pool object at', "Pool was not created at initialization")

    def test_run_item(self):
        inQ = queue.Queue()
        outQ = queue.Queue()

        inQ.put(("test name", abs, (-10, )))

        loom.run_item(inQ, outQ)

        self.assertTrue(inQ.empty(), "run_item did not remove item from todo queue")
        self.assertEqual(outQ.qsize(), 1, "run_item did not add item to done queue")
        self.assertEqual(outQ.get(), ("test name", 10), "run_item did not process the output correctly")

    def test_progress_and_is_done(self):
        rounds = multiprocessing.cpu_count()
        l = loom.loom(rounds)

        target = {}
        for i in range(1, rounds + 1):
            target[str(i)] = [i]

        l.run(time.sleep, target)

        self.assertAlmostEqual(l.progress(), 0.0)
        self.assertFalse(l.is_done())
        time.sleep(1.2)

        for i in range(1, rounds + 1):
            self.assertAlmostEqual(l.progress(), float(i) / rounds)
            self.assertFalse(l.is_done()) if i != rounds else self.assertTrue(l.is_done())
            time.sleep(1)



if __name__ == '__main__':
    unittest.main()