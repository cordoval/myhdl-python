from myhdl import *

from test_longdiv import test_longdiv

if __name__ == '__main__':    
    sim = Simulation(test_longdiv(nrvectors=2**12))
    sim.run()

