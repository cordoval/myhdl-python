import os
path = os.path
import unittest
from unittest import TestCase
import random
from random import randrange
# random.seed(2)

from myhdl import *

N = 8
M = 2 ** N
DEPTH = 5

def XorGate(z, a, b, c):
    while 1:
        yield a, b, c
        z.next = a ^ b ^ c
        
def XorGate(z, a, b, c):
    def logic():
        while 1:
            yield a, b, c
            z.next = a ^ b ^ c
    return logic()

def randOthers(i, n):
    l = range(n)
    l.remove(i)
    random.shuffle(l)
    return l[0], l[1]


def RandomScramblerModule(ol, il, stage=0):
    """ Recursive hierarchy of random xor gates.

    An invented module to check hierarchy with toVerilog.

    """

    sl1 = [Signal(bool()) for i in range(N)]
    sl2 = [Signal(bool()) for i in range(N)]
    i1 = [None] * N
    i2 = [None] * N

    if stage < DEPTH:
        for i in range(N):
            j, k = randOthers(i, N)
            i1[i] = XorGate(sl1[i], il[i], il[j], il[k])
        rs = RandomScramblerModule(sl2, sl1, stage=stage+1)
        for i in range(N):
            j, k = randOthers(i, N)
            i2[i] = XorGate(ol[i], sl2[i], sl2[j], sl2[k])
        return i1, i2, rs
    else:
        for i in range(N):
            j, k = randOthers(i, N)
            i1[i] = XorGate(ol[i], il[i], il[j], il[k])
        return i1
    

def RandomScrambler(o7, o6, o5, o4, o3, o2, o1, o0,
                    i7, i6, i5, i4, i3, i2, i1, i0):
    sl1 = [i7, i6, i5, i4, i3, i2, i1, i0]
    sl2 = [o7, o6, o5, o4, o3, o2, o1, o0]    
    rs = RandomScramblerModule(sl2, sl1, stage=0)
    return rs
    
o7, o6, o5, o4, o3, o2, o1, o0 = [Signal(bool()) for i in range(N)]
i7, i6, i5, i4, i3, i2, i1, i0 = [Signal(bool()) for i in range(N)]
v7, v6, v5, v4, v3, v2, v1, v0 = [Signal(bool()) for i in range(N)]

        
objfile = "rs.o"         
analyze_cmd = "iverilog -o %s rs.v tb_rs.v" % objfile
simulate_cmd = "vvp -m ../../../cosimulation/icarus/myhdl.vpi %s" % objfile
      
 
def RandomScrambler_v(o7, o6, o5, o4, o3, o2, o1, o0,
                      i7, i6, i5, i4, i3, i2, i1, i0):
    if path.exists(objfile):
        os.remove(objfile)
    os.system(analyze_cmd)
    return Cosimulation(simulate_cmd, **locals())


class TestRandomScramber(TestCase):

    def stimulus(self):
        input = intbv()
        output = intbv()
        output_v = intbv()
        for i in range(100):
            input[:] = randrange(M)
            i7.next = input[7]
            i6.next  = input[6]
            i5.next  = input[5]
            i4.next  = input[4]
            i3.next  = input[3]
            i2.next  = input[2]
            i1.next  = input[1]
            i0.next  = input[0]
            yield delay(10)
            output[7] = o7
            output[6] = o6
            output[5] = o5
            output[4] = o4
            output[3] = o3
            output[2] = o2
            output[1] = o1
            output[0] = o0
            output_v[7] = o7
            output_v[6] = o6
            output_v[5] = o5
            output_v[4] = o4
            output_v[3] = o3
            output_v[2] = o2
            output_v[1] = o1
            output_v[0] = o0
##             print output
##             print output_v
##             print input
            self.assertEqual(output, output_v)

    def test(self):
        rs = toVerilog(RandomScrambler, 
                       o7, o6, o5, o4, o3, o2, o1, o0,
                       i7, i6, i5, i4, i3, i2, i1, i0
                       )
        rs_v = RandomScrambler_v(v7, v6, v5, v4, v3, v2, v1, v0,
                                 i7, i6, i5, i4, i3, i2, i1, i0
                                 )
        sim = Simulation(rs, self.stimulus(), rs_v)
        sim.run()

if __name__ == '__main__':
    unittest.main()


            
            

    

    
        


                

        

