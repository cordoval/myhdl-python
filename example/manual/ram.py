from myhdl import *

def ram(dout, din, addr, we, clk, depth=128):
    """  Ram model """
    
    mem = [Signal(intbv(0)[8:]) for i in range(depth)]
    
    @always(clk.posedge)
    def write():
        if we:
            mem[int(addr)].next = din
                
    @always_comb
    def read():
        dout.next = mem[int(addr)]

    return write, read


dout = Signal(intbv(0)[8:])
dout_v = Signal(intbv(0)[8:])
din = Signal(intbv(0)[8:])
addr = Signal(intbv(0)[7:])
we = Signal(bool(0))
clk = Signal(bool(0))

toVerilog(ram, dout, din, addr, we, clk)
