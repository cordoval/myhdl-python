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

""" Run the unit tests for Signal """

__author__ = "Jan Decaluwe <jan@jandecaluwe.com>"
__revision__ = "$Revision$"
__date__ = "$Date$"

from __future__ import generators

import random
from random import randrange
random.seed(1) # random, but deterministic
from types import GeneratorType

import unittest
from unittest import TestCase

from myhdl import instances, processes

def A(n):
    yield None

def B(n):
    yield None

def C(n):
    A_1 = A(1)
    A_2 = A(2)
    B_1 = B(1)
    return A_1, A_2, B_1

g = 3

class InstancesTest(TestCase):

    def testInstances(self):

        def D():
            yield None
        D_1 = D()
        d = 1

        A_1 = A(1)
        a = [1, 2]
        B_1 = B(1)
        b = "string"
        C_1 = C(1)
        c = {}

        i = instances()
        # can't just construct an expected list;
        # that would become part of the instances also!
        self.assertEqual(len(i), 4)
        for e in (D_1, A_1, B_1, C_1):
            self.assert_(e in i)


class ProcessesTest(TestCase):

    def testProcesses(self):

        def D():
            yield None
        D_1 = D()
        d = 1

        def A():
            yield None
        
        a = [1, 2]

        def E():
            yield None
        B_1 = B(1)
        b = "string"
        C_1 = C(1)
        c = {}

        p = processes()
        self.assertEqual(len(p), 3)
        for e in p:
            self.assertEqual(type(e), GeneratorType)
        n = [e.gi_frame.f_code.co_name for e in p]
        for en in ['D', 'A', 'E']:
            self.assert_(en in n)
        

if __name__ == "__main__":
    unittest.main()
