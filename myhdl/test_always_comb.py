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

""" Run the unit tests for always_comb """

__author__ = "Jan Decaluwe <jan@jandecaluwe.com>"
__version__ = "$Revision$"
__date__ = "$Date$"

from __future__ import generators
import random
from random import randrange
random.seed(1) # random, but deterministic

import unittest
from unittest import TestCase
import inspect

from always_comb import always_comb, _AlwaysComb
from always_comb import ScopeError, ArgumentError, NrOfArgsError, \
                        SignalAsInoutError

from myhdl import Signal, Simulation, instances, processes, \
                  intbv, posedge, negedge, delay, StopSimulation

QUIET=1

def g():
    pass

x = Signal(0)

class AlwaysCombCompilationTest(TestCase):

    def testArgIsFunction(self):
        h = 5
        try:
            always_comb(h)
        except ArgumentError:
            pass
        else:
            self.fail()
    
    def testArgIsNormalFunction(self):
        def h():
            yield None
        try:
            always_comb(h)
        except ArgumentError:
            pass
        else:
            self.fail()

    def testArgHasNoArgs(self):
        def h(n):
            return n
        try:
            always_comb(h)
        except NrOfArgsError:
            pass
        else:
            self.fail()

    def testScope(self):
        try:
            always_comb(g)
        except ScopeError:
            pass
        else:
            self.fail()

    def testInfer1(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        u = 1
        def h():
            c.next = a
            v = u
        g = always_comb(h)
        i= g.gi_frame.f_locals['self']
        expected = ['a']
        self.assertEqual(i.inputs, expected)
        
    def testInfer2(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        u = 1
        def h():
            c.next = x
            g = a
        g = always_comb(h)
        i= g.gi_frame.f_locals['self']
        expected = ['a', 'x']
        expected.sort()
        self.assertEqual(i.inputs, expected)

    def testInfer3(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        d = Signal(0)
        u = 1
        def h():
            c.next = a + x + u
            a = 1
        g = always_comb(h)
        i= g.gi_frame.f_locals['self']
        expected = ['x']
        self.assertEqual(i.inputs, expected)

    def testInfer4(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        u = 1
        def h():
            c.next = a + x + u
            x = 1
        g = always_comb(h)
        i= g.gi_frame.f_locals['self']
        expected = ['a']
        self.assertEqual(i.inputs, expected)
        
        
    def testInfer5(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        def h():
            c.next += 1
            a = 1
        try:
            g = always_comb(h)
        except SignalAsInoutError:
            pass
        else:
            self.fail()

    def testInfer6(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        def h():
            c.next = a
            x.next = c
        try:
            g = always_comb(h)
        except SignalAsInoutError:
            pass
        else:
            self.fail()

    def testInfer7(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        def h():
            c.next[a:0] = x[b:0]
        g = always_comb(h)
        i= g.gi_frame.f_locals['self']
        expected = ['a', 'b', 'x']
        expected.sort()
        self.assertEqual(i.inputs, expected)
        
    def testInfer8(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        u = 1
        def h():
            v = 2
            c.next[8:1+a+v] = x[4:b*3+u]
        g = always_comb(h)
        i= g.gi_frame.f_locals['self']
        expected = ['a', 'b', 'x']
        expected.sort()
        self.assertEqual(i.inputs, expected)
         
    def testInfer9(self):
        a, b, c, d = [Signal(0) for i in range(4)]
        def h():
            c.next[a-1] = x[b-1]
        g = always_comb(h)
        i= g.gi_frame.f_locals['self']
        expected = ['a', 'b', 'x']
        expected.sort()
        self.assertEqual(i.inputs, expected)


class AlwaysCombSimulationTest(TestCase):

    def bench(self, function):

        clk = Signal(0)
        a = Signal(0)
        b = Signal(0)
        c = Signal(0)
        d = Signal(0)
        z = Signal(0)
        vectors = [intbv(j) for i in range(8) for j in range(16)]
        random.shuffle(vectors)
        
        def combfunc():
            x.next = function(a, b, c, d)

        comb = always_comb(combfunc)

        def clkGen():
            while 1:
                yield delay(10)
                clk.next ^= 1

        def logic():
            while 1:
                z.next = function(a, b, c, d)
                yield a, b, c, d

        def stimulus():
            for v in vectors:
                a.next = v[0]
                b.next = v[1]
                c.next = v[2]
                d.next = v[3]
                yield posedge(clk)
                yield negedge(clk)
                self.assertEqual(x, z)
            raise StopSimulation, "always_comb simulation test"

        return instances(), processes()

    def testAnd(self):
        def andFunction(a, b, c, d):
            return a & b & c & d
        Simulation(self.bench(andFunction)).run(quiet=QUIET)
        
    def testOr(self):
        def orFunction(a, b, c, d):
            return a | b | c | d
        Simulation(self.bench(orFunction)).run(quiet=QUIET)
        
    def testXor(self):
        def xorFunction(a, b, c, d):
            return a ^ b ^ c ^ d
        Simulation(self.bench(xorFunction)).run(quiet=QUIET)

    def testMux(self):
        def muxFunction(a, b, c, d):
            if c:
                return a
            else:
                return b
        Simulation(self.bench(muxFunction)).run(quiet=QUIET)

    def testLogic(self):
        def function(a, b, c, d):
            return not (a & (not b)) | ((not c) & d)
        Simulation(self.bench(function)).run(quiet=QUIET)



if __name__ == "__main__":
    unittest.main()
