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
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

""" myhdl package initialization.

This module provides the following myhdl objects:
Simulation -- simulation class
StopStimulation -- exception that stops a simulation
now -- function that returns the current time
Signal -- class to model hardware signals
delay -- callable to model delay in a yield statement
posedge -- callable to model a rising edge on a signal in a yield statement
negedge -- callable to model a falling edge on a signal in a yield statement
join -- callable to join clauses in a yield statement
intbv -- mutable integer class with bit vector facilities
downrange -- function that returns a downward range
Error -- myhdl Error exception
bin -- returns a binary string representation.
       The optional width specifies the desired string
       width: padding of the sign-bit is used.
concat -- function to concat ints, bitstrings, bools, intbvs, Signals
       -- returns an intbv
instances -- function that returns all instances defined in a function
always_comb -- function that returns an input-sensitive generator

"""

__author__ = "Jan Decaluwe <jan@jandecaluwe.com>"
__revision__ = "$Revision$"
__date__ = "$Date$"

__version__ = "0.3"

from _bin import bin
from _concat import concat
from _intbv import intbv
from _join import join
from _Signal import posedge, negedge, Signal
from _simulator import now
from _delay import delay
from _util import downrange, Error, StopSimulation
from _Cosimulation import Cosimulation
from _Simulation import Simulation
from _misc import instances, processes
from _always_comb import always_comb
from _enum import enum
from _traceSignals import traceSignals

