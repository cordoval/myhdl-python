import os
path = os.path
import unittest
from random import randrange

from myhdl import *
from myhdl._toVerilog import ToVerilogError, _error

b = c = 2

def UnboundError1(a, out):
    while 1:
        yield a
        out.next = a + b
        b = 1

def UnboundError2(a, out):
    while 1:
        yield a
        if a == 1:
            c = 1
        else:
            out.next = c

def UnboundError3(a, out):
    while 1:
        yield a
        out.next = a + d
        d = 1

def UnboundError4(a, out):
    while 1:
        yield a
        if a == 1:
            e = 1
        else:
            out.next = e

def InferError1(a, out):
    yield a
    b = 2
    b = intbv(0)[5:]
    b[:] = 4
    out.next = b
    
def InferError2(a, out):
    yield a
    c = intbv(0)[5:]
    c[:] = 4
    c = intbv(0)[4:]
    c[:] = 4
    out.next = c

enumType = enum("a", "b", "c")

def InferError3(a, out):
    yield a
    d = enumType.a
    d = 4
    out.next = b

def InferError4(a, out):
    h = intbv(0)
    yield a
    out.next = h

def InferError5Func(a):
    h = intbv(0)[5:]
    if a:
        return h
    else:
        return 1

def InferError5(a, out):
    yield a
    out.next = InferError5Func(a)
    
def InferError6Func(a):
    if a:
        return intbv(0)
    else:
        return intbv(1)

def InferError6(a, out):
    yield a
    out.next = InferError6Func(a)
    
def InferError7Func(a):
    if a:
        return intbv(0)[5:]
    else:
        return intbv(0xff)[7:2]

def InferError7(a, out):
    yield a
    out.next = InferError7Func(a)


class TestErrors(unittest.TestCase):
    
    def check(self, *args):
        try:
            i = toVerilog(*args)
        except ToVerilogError, e:
            self.assertEqual(e.kind, _error.NotSupported)
        except:
            self.fail()
        else:
            self.fail()

    def check(self, Infertest, err):
        a = Signal(intbv(-1)[16:])
        out_v = Signal(intbv(0)[16:])
        out = Signal(intbv(0)[16:])
        try:
            infertest_inst = toVerilog(Infertest, a, out)
        except ToVerilogError, e:
            self.assertEqual(e.kind, err)
        except:
            self.fail()
        else:
            self.fail()

    def nocheck(self, Infertest, err=None):
        a = Signal(intbv(-1)[16:])
        out_v = Signal(intbv(0)[16:])
        out = Signal(intbv(0)[16:])
        infertest_inst = toVerilog(Infertest, a, out)


    def testUnboundError1(self):
        sim = self.check(UnboundError1, _error.UnboundLocal)
        
    def testUnboundError2(self):
        sim = self.check(UnboundError2, _error.UnboundLocal)
        
    def testUnboundError3(self):
        sim = self.check(UnboundError3, _error.UnboundLocal)
        
    def testUnboundError4(self):
        sim = self.check(UnboundError4, _error.UnboundLocal)
        
    def testInferError1(self):
        sim = self.check(InferError1, _error.TypeMismatch)
        
    def testInferError2(self):
        sim = self.check(InferError2, _error.NrBitsMismatch)
        
    def testInferError3(self):
        sim = self.check(InferError3, _error.TypeMismatch)

    def testInferError4(self):
        sim = self.check(InferError4, _error.IntbvBitWidth)
        
    def testInferError5(self):
        sim = self.check(InferError5, _error.ReturnTypeMismatch)
        
    def testInferError6(self):
        sim = self.check(InferError6, _error.ReturnIntbvBitWidth)
        
    def testInferError7(self):
        sim = self.nocheck(InferError7, _error.ReturnIntbvBitWidth)
        


def Infer1(a, out):
    yield a
    c = 5
    c = a < 4
    c = bool(0)
    c = False
    c = not a
    c = True
    out.next = c
    
def Infer2(a, out):
    yield a
    c = a < 4
    c = bool(0)
    c = False
    c = not a
    c = True
    c = 5
    out.next = c

def Infer3Func(a):
    if True:
        return a > 0
    else:
        return 5

def Infer3(a, out):
    yield a
    out.next = Infer3Func(a)
    
def Infer4Func(a):
    if True:
        return 6
    else:
        return a < 3

def Infer4(a, out):
    yield a
    out.next = Infer4Func(a)

def Infer5(a, out):
    yield a
    c = a + 1
    c = a - 1
    c = a * 3
    c = a // 2
    c = a << 2
    c = a >> 2
    c = a % 16
    c = + a
    c = -( - a)
    c = ~(-3)
    c = not a
    c = 5 & 4
    c = 5 | 2
    c = 6 ^ 3
    c = bool(a and 1)
    out.next = c


     
objfile = "infertest.o"           
analyze_cmd = "iverilog -o %s infertest_inst.v tb_infertest_inst.v" % objfile
simulate_cmd = "vvp -m ../../../cosimulation/icarus/myhdl.vpi %s" % objfile
        
def Infertest_v(a, out):
    if path.exists(objfile):
        os.remove(objfile)
    os.system(analyze_cmd)
    return Cosimulation(simulate_cmd, **locals())

class TestInfer(unittest.TestCase):

    def bench(self, Infertest):
        
        a = Signal(intbv(-1)[16:])
        out_v = Signal(intbv(0)[16:])
        out = Signal(intbv(0)[16:])

        infertest_inst = toVerilog(Infertest, a, out)
        # infertest_inst = Infertest(hec, header)
        infertest_v_inst = Infertest_v(a, out_v)
 
        def stimulus():
            a.next = 1
            yield delay(10)
            print "%s %s" % (out, out_v)
            self.assertEqual(out, out_v)

        return stimulus(), infertest_inst, infertest_v_inst

    def testInfer1(self):
        sim = self.bench(Infer1)
        Simulation(sim).run()
        
    def testInfer2(self):
        sim = self.bench(Infer2)
        Simulation(sim).run()
        
    def testInfer3(self):
        sim = self.bench(Infer3)
        Simulation(sim).run()

    def testInfer4(self):
        sim = self.bench(Infer4)
        Simulation(sim).run()
        
    def testInfer5(self):
        sim = self.bench(Infer5)
        Simulation(sim).run()

        
if __name__ == '__main__':
    unittest.main()
