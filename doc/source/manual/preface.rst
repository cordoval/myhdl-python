*******
Preface
*******


The goal of the MyHDL project is to empower hardware designers with the elegance
and simplicity of the Python language.

MyHDL is a free, open-source (LGPL) package for using Python as a hardware
description and verification language. Python is a very high level language, and
hardware designers can use its full power to model and simulate their designs.
Moreover, MyHDL can convert a design to Verilog or VHDL. In combination with an external
synthesis tool, this provides a complete path from Python to a silicon
implementation.

*Modeling*

Python's power and clarity make MyHDL an ideal solution for high level modeling.
Python is famous for enabling elegant solutions to complex modeling problems.
Moreover, Python is outstanding for rapid application development and
experimentation.

The key idea behind MyHDL is the use of Python generators to model hardware
concurrency. Generators are best described as resumable functions. In MyHDL,
generators are used in a specific way so that they become similar to always
blocks in Verilog or processes in VHDL.

A hardware module is modeled as a function that returns any number of
generators. This approach makes it straightforward to support features such as
arbitrary hierarchy, named port association, arrays of instances, and
conditional instantiation.

Furthermore, MyHDL provides classes that implement traditional hardware
description concepts. It provides a signal class to support communication
between generators, a class to support bit oriented operations, and a class for
enumeration types.

*Simulation and Verification*

The built-in simulator runs on top of the Python interpreter. It supports
waveform viewing by tracing signal changes in a VCD file.

With MyHDL, the Python unit test framework can be used on hardware designs.
Although unit testing is a popular modern software verification technique, it is
not yet common in the hardware design world, making it one more area in which
MyHDL innovates.

MyHDL can also be used as hardware verification language for Verilog
designs, by co-simulation with traditional HDL simulators.

*Conversion to Verilog and VHDL*

MyHDL designs can be converted to Verilog or VHDL, if certain coding
restrictions are obeyed.
The conversion works on an instantiated design that has been fully
elaborated. Consequently, the original design structure can be arbitrarily
complex.

