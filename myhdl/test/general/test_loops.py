import os
path = os.path
from random import randrange


from myhdl import *
from myhdl.conversion import verify, analyze
from myhdl import ConversionError
from myhdl.conversion._misc import _error

def ForLoopError1(a, out):
    while 1:
        yield a
        var = 0
        for i in (1, 2, 3):
            if a[i] == 1:
                var += 1
        out.next = var
        
def ForLoopError2(a, out):
    while 1:
        yield a
        var = 0
        for i in list((1, 2, 3)):
            if a[i] == 1:
                var += 1
        out.next = var


def ForLoop1(a, out):
    while 1:
        yield a
        var = 0
        for i in downrange(len(a)):
            if a[i] == 1:
                var += 1
        out.next = var

def ForLoop2(a, out):
    while 1:
        yield a
        var = 0
        for i in downrange(len(a), 5):
            if a[i] == 1:
                var += 1
        out.next = var

def ForLoop3(a, out):
    while 1:
        yield a
        var = 0
        for i in downrange(len(a), 3, 2):
            if a[i] == 1:
                var += 1
        out.next = var
        
def ForLoop4(a, out):
    while 1:
        yield a
        var = 0
        for i in range(len(a)):
            if a[i] == 1:
                var += 1
        out.next = var

def ForLoop5(a, out):
    while 1:
        yield a
        var = 0
        for i in range(6, len(a)):
            if a[i] == 1:
                var += 1
        out.next = var

def ForLoop6(a, out):
    while 1:
        yield a
        var = 0
        for i in range(5, len(a), 3):
            if a[i] == 1:
                var += 1
        out.next = var

def ForContinueLoop(a, out):
    while 1:
        yield a
        var = 0
        for i in downrange(len(a)):
            if a[i] == 0:
                continue
            var += 1
        out.next = var

def ForBreakLoop(a, out):
    while 1:
        yield a
        out.next = 0
        for i in downrange(len(a)):
            if a[i] == 1:
                out.next = i
                break

def ForBreakContinueLoop(a, out):
    while 1:
        yield a
        out.next = 0
        for i in downrange(len(a)):
            if a[i] == 0:
                continue
            out.next = i
            break

def NestedForLoop1(a, out):
    while 1:
        yield a
        var = 0
        for i in downrange(len(a)):
            if a[i] == 0:
                continue
            else:
                for j in downrange(i):
                    if a[j] == 0:
                        var +=1
                break
        out.next = var

def NestedForLoop2(a, out):
    while 1:
        yield a
        var = 0
        out.next = 0
        for i in downrange(len(a)):
            if a[i] == 0:
                continue
            else:
                for j in downrange(i-1):
                    if a[j] == 0:
                        pass
                    else:
                        out.next = j
                        break
                break

def ReturnFromFunction(a):
       for i in downrange(len(a)):
            if a[i] == 1:
                return i
       return 0

def FunctionCall(a, out):
    while 1:
        yield a
        out.next = ReturnFromFunction(a)

# During the following check, I noticed that non-blocking assignments
# are not scheduled when a task is disabled in Icarus. Apparently
# this is one of the many vague areas in the Verilog standard.
def ReturnFromTask(a, out):
    for i in downrange(len(a)):
        if a[i] == 1:
            out[:] = i
            return
    out[:] = 23 # to notice it

def TaskCall(a, out):
    var = intbv(0)[8:]
    while 1:
        yield a
        ReturnFromTask(a, var)
        out.next = var

def WhileLoop(a, out):
    while 1:
        yield a
        var = 0
        i = len(a)-1
        while i >= 0:
            if a[i] == 1:
                var += 1
            i -= 1
        out.next = var

def WhileContinueLoop(a, out):
    while 1:
        yield a
        var = 0
        i = len(a)-1
        while i >= 0:
            if a[i] == 0:
                i -= 1
                continue
            var += 1
            i -= 1
        out.next = var
        
def WhileBreakLoop(a, out):
    while 1:
        yield a
        var = 0
        i = len(a)-1
        out.next = 0
        while i >= 0:
            if a[i] == 1:
                out.next = i
                break
            i -= 1
    
def WhileBreakContinueLoop(a, out):
    while 1:
        yield a
        var = 0
        i = len(a)-1
        out.next = 0
        while i >= 0:
            if a[i] == 0:
                 i -= 1
                 continue
            out.next = i
            break
    


def LoopBench(LoopTest):

    a = Signal(intbv(-1)[16:])
    z = Signal(intbv(0)[16:])

    looptest_inst = LoopTest(a, z)
    data = tuple([randrange(2**min(i, 16)) for i in range(100)])

    @instance
    def stimulus():
        for i in range(100):
            a.next = data[i]
            yield delay(10)
            print z

    return stimulus, looptest_inst



def testForLoop1():
    assert verify(LoopBench, ForLoop1) == 0
def testForLoop2():
    assert verify(LoopBench, ForLoop2) == 0
def testForLoop4():
    assert verify(LoopBench, ForLoop4) == 0
def testForLoop5():
    assert verify(LoopBench, ForLoop5) == 0

# for loop 3 and 6 can't work in vhdl

def testForContinueLoop():
  assert verify(LoopBench, ForContinueLoop) == 0

def testForBreakLoop():
   assert verify(LoopBench, ForBreakLoop) == 0

def testForBreakContinueLoop():
   assert verify(LoopBench, ForBreakContinueLoop) == 0

def testNestedForLoop1():
   assert verify(LoopBench, NestedForLoop1) == 0

def testNestedForLoop2():
   assert verify(LoopBench, NestedForLoop2) == 0

def testWhileLoop():
    assert verify(LoopBench, FunctionCall) == 0

## def testTaskCall(self):
##     sim = self.bench(TaskCall)
##     Simulation(sim).run()

def testWhileLoop():
    assert verify(LoopBench, WhileLoop) == 0

def testWhileContinueLoop():
    assert verify(LoopBench, WhileContinueLoop) == 0

def testWhileBreakLoop():
    assert verify(LoopBench, WhileBreakLoop) == 0

def testWhileBreakContinueLoop():
    assert verify(LoopBench, WhileBreakContinueLoop) == 0

def testForLoopError1():
    try:
        analyze(LoopBench, ForLoopError1)
    except ConversionError, e:
        assert e.kind == _error.Requirement
    else:
        assert False
    
def testForLoopError2():
    try:
        analyze(LoopBench, ForLoopError2)
    except ConversionError, e:
        assert e.kind == _error.Requirement
    else:
        assert False
    
    

