#  This file is part of the myhdl library, a Python package for using
#  Python as a Hardware Description Language.
#
#  Copyright (C) 2003 Jan Decaluwe
#
#  The myhdl library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation; either version 2.1 of the
#  License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.

#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

""" Run the unit tests for bin """

__author__ = "Jan Decaluwe <jan@jandecaluwe.com>"
__revision__ = "$Revision$"
__date__ = "$Date$"

from __future__ import generators

import random
from random import randrange
random.seed(1) # random, but deterministic
import sys
import os
path = os.path

import unittest
from unittest import TestCase
import shutil

from myhdl import delay, Signal, Simulation
from myhdl._traceSignals import traceSignals, TopLevelNameError, ArgTypeError, \
                              NoInstancesError

QUIET=1

def gen(clk):
    while 1:
        yield delay(10)
        clk.next = not clk

def fun():
    clk = Signal(bool(0))
    inst = gen(clk)
    return inst

def dummy():
    clk = Signal(bool(0))
    inst = gen(clk)
    return 1

def top():
    inst = traceSignals(fun)
    return inst

def top2():
    inst = [{} for i in range(4)]
    j = 3
    inst[j-2]['key'] = traceSignals(fun)
    return inst


class TestTraceSigs(TestCase):

    def setUp(self):
        self.paths = paths = ["dut.vcd", "inst.vcd"]
        for p in paths:
            if path.exists(p):
                os.remove(p)

    def tearDown(self):
        for p in self.paths:
            if path.exists(p):
                os.remove(p)

    def testTopName(self):
        p = "dut.vcd"
        dut = traceSignals(fun)
        try:
            traceSignals(fun)
        except TopLevelNameError:
            pass
        else:
            self.fail()

    def testArgType1(self):
        p = "dut.vcd"
        try:
            dut = traceSignals([1, 2])
        except ArgTypeError:
            pass
        else:
            self.fail()
            
    def testArgType2(self):
        p = "dut.vcd"
        try:
            dut = traceSignals(gen, Signal(0))
        except ArgTypeError:
            pass
        else:
            self.fail()

    def testReturnVal(self):
        p = "dut.vcd"
        try:
            dut = traceSignals(dummy)
        except NoInstancesError:
            pass
        else:
            self.fail()
            
    def testHierarchicalTrace1(self):
        p = "inst.vcd"
        top()
        self.assert_(path.exists(p))
        
    def testHierarchicalTrace2(self):
        pdut = "dut.vcd"
        psub = "inst.vcd"
        dut = traceSignals(top)
        self.assert_(path.exists(pdut))
        self.assert_(not path.exists(psub))

    def testIndexedName(self):
        p = "dut[1][0].vcd"
        dut = [[None] * 3 for i in range(4)]
        i, j = 0, 2
        dut[i+1][j-2] = traceSignals(top)
        self.assert_(path.exists(p))
        os.remove(p)

    def testIndexedName2(self):
        p = "inst[1][key].vcd"
        top2()
        self.assert_(path.exists(p))
        os.remove(p)

    def testBackupOutputFile(self):
        p = "dut.vcd"
        dut = traceSignals(fun)
        Simulation(dut).run(1000, quiet=QUIET)
        size = path.getsize(p)
        pbak = p + '.' + str(path.getmtime(p))
        self.assert_(not path.exists(pbak))
        dut = traceSignals(fun)
        self.assert_(path.exists(p))
        self.assert_(path.exists(pbak))
        self.assert_(path.getsize(pbak) == size)
        self.assert_(path.getsize(p) < size)
        os.remove(pbak)
       
if __name__ == "__main__":
    unittest.main()
