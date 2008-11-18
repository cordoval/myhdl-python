
.. currentmodule:: myhdl

.. _conv:

******************************
Conversion to Verilog and VHDL
******************************


.. _conv-intro:

Introduction
============

Subject to some limitations, 
MyHDL supports the automatic conversion of MyHDL code to
Verilog or VHDL code. This feature provides a path from MyHDL into a
standard Verilog or VHDL based design environment.

This chapter describes the concepts of conversion. Concrete
examples can be found in the companion chapter :ref:`conv-usage`.

.. _conv-solution:

Solution description
====================

To be convertible, the hardware description should satisfy certain restrictions,
defined as the :dfn:`convertible subset`. This is described
in detail in :ref:`conv-subset`.

A convertible design can be converted to an equivalent model in Verilog
or VHDL, using the function :func:`toVerilog` or :func:`toVHDL`  from the MyHDL 
library. 

When the design is intended for implementation
a third-party :dfn:`synthesis tool` is used to convert the Verilog or VHDL
design to a gate implementation for an ASIC or FPGA. With this step, there is
a path from a hardware description in  Python to an FPGA or ASIC implementation.

The conversion does not start from source files, but from an instantiated design
that has been *elaborated* by the Python interpreter. The converter uses the
Python profiler to track the interpreter's operation and to infer the design
structure and name spaces. It then selectively compiles pieces of source code
for additional analysis and for conversion.

.. _conv-features:

Features
========


Conversion after elaboration
  *Elaboration* refers to the initial processing of a hardware description to
  achieve a representation of a design instance that is ready for simulation or
  synthesis. In particular, structural parameters and constructs are processed in
  this step. In MyHDL, the Python interpreter itself is used for elaboration.  A
  :class:`Simulation` object is constructed with elaborated design instances as
  arguments.  Likewise, conversion works on an elaborated design
  instance. The Python interpreter is thus used as much as possible.

Arbitrarily complex structure
  As the conversion works on an elaborated design instance, any modeling
  constraints only apply to the leaf elements of the design structure, that is,
  the co-operating generators. In other words, there are no restrictions on the
  description of the design structure: Python's full power can be used for that
  purpose. Also, the design hierarchy can be arbitrarily deep.

Generator are mapped to Verilog or VHDL constructs
  The converter analyzes the code of each generator and maps it to equivalent
  constructs in the target HDL. For Verilog, it will map generators to
  ``always`` blocks, continuous assignments or ``initial`` blocks. For VHDL,
  it will map them to ``process`` statements or concurrent signal assignments.

The module interface is inferred from signal usage
  In MyHDL, the input or output direction of interface signals is not explicitly
  declared. The converter investigates signal usage in the design hierarchy to
  infer whether a signal is used as input, output, or as an internal signal.

Function calls are mapped to Verilog or VHDL subprograms
  The converter analyzes function calls and function code. Each function is
  mapped to an appropriate subprograms in the target HDL:  a function or task in  Verilog,
  and a function  or procedure in VHDL.
  In order to support the full power of Python functions,
  a unique subprogram is generated per Python function call.

If-then-else structures may be mapped to case statements
  Python does not provide a case statement. However,  the converter recognizes if-then-else
  structures in which a variable is sequentially compared to items of an
  enumeration type, and maps such a structure to a Verilog or VHDL case statement with the
  appropriate synthesis attributes.

Choice of encoding schemes for enumeration types
  The :func:`enum` function in MyHDL returns an enumeration type. This function
  takes an additional parameter *encoding* that specifies the desired encoding in
  the implementation: binary, one hot, or one cold. The converter
  generates the appropriate code for the specified encoding.

RAM memory
  Certain synthesis tools can map Verilog memories or VHDL arrays to RAM structures. To support
  this interesting feature, the converter maps lists of signals to Verilog
  memories or VHDL arrays.

ROM memory
  Some synthesis tools can infer a ROM from a case statement. The
  converter does the expansion into a case statement automatically, based on a
  higher level description. The ROM access is described in a single line, by
  indexing into a tuple of integers.

Signed arithmetic
  In MyHDL, working with negative numbers is trivial: one just uses an
  ``intbv`` object with an appropriate constraint on its values.  In
  contrast, both Verilog and VHDL make a difference between an
  unsigned and a signed representation. To work with negative values,
  the user has to declare a signed variable explicitly. But when
  signed and unsigned operands are mixed in an expression, things may
  become tricky.

  In Verilog, when signed and unsigned operands are mixed, all
  operands are interpreted as *unsigned*. Obviously, this leads to
  unexpected results. The designer will have to add sign extensions
  and type casts to solve this.

  In VHDL, mixing signed and unsigned will generally not work. The
  designer will have to match the operands manually by adding
  resizings and type casts.

  In MyHDL, these issues don't exist because ``intbv`` objects simply
  work as (constrained) integers. Moreover, the convertor automates
  the cumbersome tasks that are required in Verilog and
  VHDL. It uses signed or unsigned types based on the value
  constraints of the intbv objects, and automatically performs the
  required sign extensions, resizings, and type casts.


User-defined code
  If desired, the user can bypass the conversion process and describe
  user-defined code to be inserted instead.


.. _conv-subset:

The convertible subset
======================


.. _conv-subset-intro:

Introduction
------------

Unsurprisingly, not all MyHDL code can be converted.  Although the
restrictions are significant, the convertible subset is much broader
than the RTL synthesis subset which is an industry standard.  In other
words, MyHDL code written according to the RTL synthesis rules, should
always be convertible. However, it is also possible to write
convertible code for non-synthesizable models or test benches.

The converter attempts to issue clear error messages when it
encounters a construct that cannot be converted.

Recall that any restrictions only apply to the design after
elaboration.  In practice, this means that they apply only to the code
of the generators, that are the leaf functional blocks in a MyHDL
design.


.. _conv-subset-style:

Coding style
------------

A natural restriction on convertible code is that it should be written in MyHDL
style: cooperating generators, communicating through signals, and with
sensitivity specify resume conditions. 

For pure modeling, it doesn't matter how generator are created.
However, in convertible code they should be created using one
of the MyHDL decorators: :func:`instance`, :func:`always` or
:func:`always_comb`.


.. _conv-subset-types:

Supported types
---------------

The most important restriction regards object types.  Only a limited
amount of types can be converted. Python :class:`int` and
:class:`long` objects are mapped to Verilog or VHDL integers. All
other supported types are mapped need to have a defined bit width. The
supported types are the Python :class:`bool` type, the MyHDL
:class:`intbv` type, and MyHDL enumeration types returned by function
:func:`enum`.

:class:`intbv` objects must be constructed so that a bit width can be
inferred.  This can be done by specifying minimum and maximum values,
e.g. as follows::

   index = intbv(0, min=MIN, max=MAX)

The Verilog converter supports :class:`intbv` objects that can take
negative values.

Alternatively, a slice can be taken from an :class:`intbv` object as
follows::

   index = intbv(0)[N:]

Such as slice returns a new :class:`intbv` object, with minimum value
``0`` , and maximum value ``2**N``.

In addition to the scalar types described above, a the convertor also
supports a number of tuple and list based types. The mapping from
MyHDL types is summarized in the following table.


+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
|  MyHDL type                                | VHDL type                     | Notes     | Verilog type                  | Notes     |
+============================================+===============================+===========+===============================+===========+
| ``int``                                    | ``integer``                   |           | ``integer``                   |           |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``bool``                                   | ``std_logic``                 | \(1)      | ``reg``                       |           |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``intbv`` with ``min >= 0``                | ``unsigned``                  | \(2)      | ``reg``                       |           |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``intbv`` with  ``min < 0``                | ``signed``                    | \(2)      | ``reg signed``                |           |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``enum``                                   | dedicated enumeration type    |           | ``reg``                       |           |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``tuple`` of ``int``                       | mapped to case statement      | \(3)      | mapped to case statement      | \(3)      |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``list`` of ``bool``                       | ``array of std_logic``        |           | ``reg``                       | \(5)      |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``list`` of ``intbv`` with ``min >= 0``    | ``array of unsigned``         | \(4)      | ``reg``                       | \(4)\(5)  |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+
| ``list`` of ``intbv`` with ``min < 0``     | ``array of signed``           | \(4)      | ``reg signed``                | \(4)\(5)  |
+--------------------------------------------+-------------------------------+-----------+-------------------------------+-----------+


Notes:

(1) 
   The VHDL ``std_logic`` type is defined in the standard VHDL package
   ``IEEE.std_logic_1164``.

(2)
   The VHDL ``unsigned`` and ``signed`` types used are those from the
   standard VHDL packages ``IEEE.numeric_std``.

(3)
   A MyHDL ``tuple`` of ``int`` is used for ROM inference, and can only be
   used in a very specific way: an indexing operation into the tuple
   should be the rhs of an assignment.

(4)
   All list members should have identical value constraints.

  
(5)
   Lists are mapped to Verilog memories. 


The table as presented applies to MyHDL variables. The convertor also
supports MyHDL signals that use ``bool``, ``intbv`` or ``enum``
objects as their underlying type. For VHDL, these are mapped to VHDL signals
with an underlying type as specified in the table above. Verilog doesn't have
the signal concept. For Verilog, a MyHDL signal is mapped to a Verilog
``reg`` as in the table above, or to a Verilog ``wire``, depending
on the signal usage.

The convertor supports MyHDL list of signals provided the underlying
signal type is either ``bool`` or ``intbv``. They may be mapped to a
VHDL signal with a VHDL type as specified in the table, or to a
Verilog memory.  However, list of signals are not always mapped to a
corresponding VHDL or Verilog object.  See :ref:`conv-listofsigs` for
more info.

.. _conv-subset-statements:

Supported statements
--------------------

The following is a list of the statements that are supported by the Verilog
converter, possibly qualified with restrictions or usage notes.

:keyword:`assert`
  An :keyword:`assert` statement in Python looks as follow::

      assert test_expression

  It can be converted provided ``test_expression`` is convertible.

:keyword:`break`

:keyword:`continue`

:keyword:`def`

:keyword:`for`
   The only supported iteration scheme is iterating through sequences of integers
   returned by built-in function :func:`range` or MyHDL function
   :func:`downrange`.  The optional :keyword:`else` clause is not supported.

:keyword:`if`
   :keyword:`if`, :keyword:`elif`, and :keyword:`else` clauses are fully supported.

:keyword:`pass`

:keyword:`print`

  A :keyword:`print` statement with multiple arguments::

      print arg1, arg2, ...

  is supported. However, there are restrictions on the arguments.
  First, they should be of one of the following forms::

      arg
      formatstring % arg
      formatstring % (arg1, arg2, ...)

  where ``arg`` is a ``bool``, ``int``, ``intbv``, ``enum``, or a
  ``Signal`` of these types.

  The ``formatstring`` contains ordinary characters and conversion
  specifiers as in Python. However, the only supported conversion specifiers
  are ``%s`` and ``%d``.
  Justification and width specification are thus not supported.

  Printing without a newline::

     print arg1 ,

  is not supported.

 
:keyword:`raise`
   This statement is mapped to statements that end the simulation with an
   error message.

:keyword:`return`

:keyword:`yield`
   A `yield` expression is used to specify a sensitivity list.
   The yielded expression can be a :class:`Signal`, a signal edge as specified by MyHDL
   functions :attr:`Signal.posedge` or :attr:`Signal.negedge`, or a tuple of signals and edge
   specifications. It can also be a :func:`delay` object.

:keyword:`while`
   The optional :keyword:`else` clause is not supported.


.. _conv-subset-builtin:

Supported built-in functions
----------------------------

The following is a list of the built-in functions that are supported by the
converter.

:func:`bool`
   This function can be used to typecast an object explictly to its boolean
   interpretation.

:func:`len`
   For :class:`Signal` and :class:`intbv` objects, function :func:`len` returns the
   bit width.

:func:`int`
   This function can be used to typecast an object explictly to its integer
   interpretation.




.. _conv-listofsigs:

Conversion of lists of signals
==============================

Lists of signals are useful for many purposes. For example, they make
it easy to create a repetitive structure. Another application is the
description of memory behavior.

The convertor output is non-hierarchical. That implies that all
signals are declared at the top-level in VHDL or Verilog (as VHDL
signals, or Verilog regs and wires.)  However, some signals that are a
list member at some level in the MyHDL design hierarchy may be used as
a plain signal at a lower level. For such signals, a choice has to be
made whether to declare a Verilog memory or VHDL array, or a number of
plain signal names.

If possible, plain signal declarations are preferred, because Verilog
memories and arrays have some restrictions in usage and tool support.
This is possible if the list syntax is strictly used outside generator
code, for example when lists of signals are used to describe
structure.

Conversely, when list syntax is used in some generator, then a Verilog
memory or VHDL array will be declared. The typical example is the
description of RAM memories.


.. _conv-meth-assign:

Assignment issues
=================


.. _conv-meth-assign-python:

Name assignment in Python
-------------------------

Name assignment in Python is a different concept than in many other languages.
This point is very important for effective modeling in Python, and even more so
for synthesizable MyHDL code. Therefore, the issues are discussed here
explicitly.

Consider the following name assignments::

   a = 4
   a = ``a string''
   a = False

In many languages, the meaning would be that an existing variable *a* gets a
number of different values. In Python, such a concept of a variable doesn't
exist. Instead, assignment merely creates a new binding of a name to a certain
object, that replaces any previous binding. So in the example, the name *a* is
bound a  number of different objects in sequence.

The converter has to investigate name assignment and usage in MyHDL
code, and to map names to Verilog or VHDL objects. To achieve that, it tries to infer
the type and possibly the bit width of each expression that is assigned to a
name.

Multiple assignments to the same name can be supported if it can be determined
that a consistent type and bit width is being used in the assignments. This can
be done for boolean expressions, numeric expressions, and enumeration type
literals.

In other cases, a single assignment should be used when an object is created.
Subsequent value changes are then achieved by modification of an existing
object.  This technique should be used for :class:`Signal` and :class:`intbv`
objects.


.. _conv-meth-assign-signal:

Signal assignment
-----------------

Signal assignment in MyHDL is implemented using attribute assignment to
attribute ``next``.  Value changes are thus modeled by modification of the
existing object. The converter investigates the :class:`Signal` object to infer
the type and bit width of the corresponding Verilog or VHDL object.


.. _conv-meth-assign-intbv:

:class:`intbv` objects
----------------------

Type :class:`intbv` is likely to be the workhorse for synthesizable
modeling in MyHDL. An :class:`intbv` instance behaves like a (mutable)
integer whose individual bits can be accessed and modified. Also, it
is possible to constrain its set of values. In addition to error
checking, this makes it possible to infer a bit width, which is
required for implementation.

As noted before, it is not possible to modify value of a an
:class:`intbv` object using name assignment. In the following, we will
show how it can be done instead.  Consider::

   a = intbv(0)[8:]

This is an :class:`intbv` object with initial value ``0`` and bit
width 8. The change its value to ``5``, we can use slice assignment::

   a[8:] = 5

The same can be achieved by leaving the bit width unspecified, which
has the meaning to change "all" bits::

   a[:] = 5

Often the new value will depend on the old one. For example, to
increment an :class:`intbv` with the technique above::

   a[:] = a + 1

Python also provides *augmented* assignment operators, which can be
used to implement in-place operations. These are supported on
:class:`intbv` objects and by the converter, so that the increment can
also be done as follows::

   a += 1




.. _conv-subset-exclude:

Excluding code from conversion
==============================

For some tasks, such as debugging, it may be useful to insert arbitratry Python
code that should not be converted.

The convertor supports this by ignoring all code that is embedded in a
``if __debug__`` test. The value of the ``__debug__`` variable is not taken into
account.


Template transformation
=======================

.. note:: This section is only revelant for VHDL.

There is a difference between VHDL and Verilog in the way in which
sensitivity to signal edges is specified. In Verilog, edge specifiers
can be used directly in the sensitivity list. In VHDL, this is not
possible: only signals can be used in the sensitivity list. To check
for an edge, one uses the ``rising_edge()`` or ``falling_edge()``
functions in the code.

MyHDL follows the Verilog scheme to specify edges in the sensitivity
list. Consequently, when mapping such code to VHDL, it needs to be
transformed to equivalent VHDL. This is an important issue because it
affects all synthesizable templates that infer sequential logic.

We will illustrate this feature with some examples. This is the MyHDL
code for a D flip-flop::


    @always(clk.posedge)
    def logic():
        q.next = d


It is converted to VHDL as follows::

    DFF_LOGIC: process (clk) is
    begin
        if rising_edge(clk) then
            q <= d;
        end if;
    end process DFF_LOGIC;


The convertor can handle the more general case. For example, this is
MyHDL code for a D flip-flop with asynchronous set, asynchronous
reset, and preference of set over reset::


    @always(clk.posedge, set.negedge, rst.negedge)
    def logic():
        if set == 0:
            q.next = 1
        elif rst == 0:
            q.next = 0
        else:
            q.next = d


This is converted to VHDL as follows::


    DFFSR_LOGIC: process (clk, set, rst) is
    begin
        if (set = '0') then
            q <= '1';
        elsif (rst = '0') then
            q <= '0';
        elsif rising_edge(clk) then
            q <= d;
        end if;
    end process DFFSR_LOGIC;


All cases with practical utility can be handled in this way. However,
there are other cases that cannot be transformed to equivalent
VHDL. The convertor will detect those cases and give an error.


.. _conv-meth-conv:

Conversion output verification by co-simulation
===============================================

.. note:: This section is only revelant for Verilog.

To verify the converted Verilog output, co-simulation can be used. To
make this task easier, the converter also generates a test bench that
makes it possible to simulate the Verilog design using the Verilog
co-simulation interface. This permits to verify the Verilog code with
the same test bench used for the MyHDL code.


.. _conv-testbench:

Conversion of test benches
==========================

After conversion, we obviously want to verify that the VHDL or Verilog
code works correctly. For Verilog, we can use co-simulation as
discussed earlier. However, for VHDL, co-simulation is currently
not supported.

An alternative is to convert the test bench itself, so that
both test bench and design can be run in the HDL simulator. Of course,
this is not a fully general solution, as there are important
constraints on the kind of code that can be converted.
Thus, the question is whether the conversion restrictions permit to develop
sufficiently complex test benches. In this section, we present some
insights about this.

The most important restrictions regard the types that can be used, as
discussed earlier in this chapter. However, the "convertible subset" is
wider than the "synthesis subset". We will present a number of
non-synthesizable feature that are of interest for test benches.

the :keyword:`while` loop
 :keyword:`while` loops can be used for high-level control structures.
 
the :keyword:`raise` statement
   A :keyword:`raise` statement can stop the simulation on an error condition.

:func:`delay()` objects
   Delay modelling is essential for test benches.

the :keyword:`print` statement
   :keyword:`print` statements can be used for simple debugging.

the :keyword:`assert` statement.
  Originally, :keyword:`assert` statements were only intended to insert debugging
  assertions in code. Recently, there is a tendency to use them to write
  self-checking unit tests, controlled by unit test frameworks such as
  ``py.test``. In particular, they are a powerful way to write
  self-checking test benches for MyHDL designs. As :keyword:`assert`
  statements are convertible, a whole unittest suite in MyHDL can be
  converted to an equivalent test suite in Verilog and VHDL.

Additionally, the same techniques as for synthesizable code can be used
to master complexity. In particular, any code outside generators
is executed during elaboration, and therefore not considered in
the conversion process. This feature can for example be used for
complex calculations that set up constants or expected results.
Furthermore, a tuple of ints can be used to hold a table of
values that will be mapped to a case statement in Verilog and VHDL.



.. _conv-meth:

Methodology notes
=================


.. _conv-meth-sim:

Simulate first
--------------

In the Python philosophy, the run-time rules. The Python compiler doesn't
attempt to detect a lot of errors beyond syntax errors, which given Python's
ultra-dynamic nature would be an almost impossible task anyway. To verify a
Python program, one should run it, preferably using unit testing to verify each
feature.

The same philosophy should be used when converting a MyHDL description to
Verilog: make sure the simulation runs fine first. Although the converter checks
many things and attempts to issue clear error messages, there is no guarantee
that it does a meaningful job unless the simulation runs fine.


.. _conv-meth-hier:

Handling hierarchy
------------------



.. _conv-issues:

Known issues
============

Verilog and VHDL integers are 32 bit wide
   Usually, Verilog and VHDL integers are 32 bit wide. In contrast,
   Python is moving toward integers with undefined width. Python
   :class:`int` and :class:`long` variables are mapped to Verilog
   integers; so for values wider than 32 bit this mapping is
   incorrect.

Synthesis pragmas are specified as Verilog comments.
   The recommended way to specify synthesis pragmas in Verilog is
   through attribute lists. However, the Icarus simulator doesn't
   support them for ``case`` statements (to specify ``parallel_case``
   and ``full_case`` pragmas). Therefore, the old but deprecated
   method of synthesis pragmas in Verilog comments is still used.

Inconsistent place of the sensitivity list inferred from ``always_comb``.
   The semantics of ``always_comb``, both in Verilog and MyHDL, is to
   have an implicit sensitivity list at the end of the code. However,
   this may not be synthesizable. Therefore, the inferred sensitivity
   list is put at the top of the corresponding ``always`` block or
   ``process``. This may cause inconsistent behavior at the start of
   the simulation. The workaround is to create events at time 0.


