from myhdl import *
from myhdl import ConversionError
from myhdl.conversion._misc import _error
from myhdl.conversion import verify


def sigAugmAssignUnsupported(z, a):
    @always(a)
    def logic():
        z.next += a
    return logic

def test_SigAugmAssignUnsupported():
    z = Signal(intbv(0)[8:])
    a = Signal(intbv(0)[8:])
    try:
        verify(sigAugmAssignUnsupported, z, a)
    except ConversionError, e:
        assert e.kind == _error.NotSupported
    else:
        assert False
        
def modbvRange(z, a, b):
    @always(a, b)
    def logic():
        s = modbv(0, min=0, max=35)
        s[:] = a + b
        z.next = s
    return logic

def test_modbvRange():
    z = Signal(intbv(0)[8:])
    a = Signal(intbv(0)[4:])
    b = Signal(intbv(0)[4:])
    try:
        verify(modbvRange, z, a, b)
    except ConversionError, e:
        assert e.kind == _error.ModbvRange
    else:
        assert False
        


