import unittest
import os
path = os.path
from random import randrange

from myhdl import *

# example from Frank Palazollo
def or_gate(a,b,c):
    while 1:
        c.next = a | b
        yield a, b
        
def my_bundle(p,q):
	r = Signal(bool(0))
	gen_or = or_gate(p,r,q)
	return instances()

# additional level of hierarchy
def ConstWire2(p, q):
    r = Signal(bool(1))
    s = Signal(bool(1))
    inst1 = my_bundle(p, r)
    inst2 = or_gate(r, s, q)
    return inst1, inst2

def adder(a, b, c):
    while 1:
        yield a, b
        c.next = a + b

def ConstWire3(p, q):
    t = Signal(intbv(17)[5:])
    adder_inst = adder(p, t, q)
    return instances()
    

objfile = "constwire.o"           
analyze_cmd = "iverilog -o %s constwire_inst.v tb_constwire_inst.v" % objfile
simulate_cmd = "vvp -m ../../../cosimulation/icarus/myhdl.vpi %s" % objfile
        
def ConstWire_v(p, q):
    if path.exists(objfile):
        os.remove(objfile)
    os.system(analyze_cmd)
    return Cosimulation(simulate_cmd, **locals())

class TestConstWires(unittest.TestCase):

    def benchBool(self, ConstWire):
        
        p = Signal(bool(0))
        q = Signal(bool(0))
        q_v = Signal(bool(0))

        constwire_inst = toVerilog(ConstWire, p, q)
        constwire_v_inst = ConstWire_v(p, q_v)

        def stimulus():
            for i in range(100):
                p.next = randrange(2)
                yield delay(10)
                self.assertEqual(q, q_v)

        return stimulus(), constwire_inst, constwire_v_inst

    def testConstWire1(self):
        sim = self.benchBool(my_bundle)
        Simulation(sim).run()

    def testConstWire2(self):
        sim = self.benchBool(ConstWire2)
        Simulation(sim).run()        

    def benchIntbv(self, ConstWire):
        
        p = Signal(intbv(0)[8:])
        q = Signal(intbv()[8:])
        q_v = Signal(intbv()[8:])

        constwire_inst = toVerilog(ConstWire, p, q)
        constwire_v_inst = ConstWire_v(p, q_v)

        def stimulus():
            for i in range(100):
                p.next = i
                yield delay(10)
                self.assertEqual(q, q_v)
                
        return stimulus(), constwire_inst, constwire_v_inst
        
    def testConstWire3(self):
        sim = self.benchIntbv(ConstWire3)
        Simulation(sim).run()
        
        
if __name__ == '__main__':
    unittest.main()
