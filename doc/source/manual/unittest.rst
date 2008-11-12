.. currentmodule:: myhdl

.. _unittest:

************
Unit testing
************


.. _unittest-intro:

Introduction
============

Many aspects in the design flow of modern digital hardware design can be viewed
as a special kind of software development. From that viewpoint, it is a natural
question whether advances in software design techniques can not also be applied
to hardware design.

.. index:: single: extreme programming

One software design approach that gets a lot of attention recently is *Extreme
Programming* (XP). It is a fascinating set of techniques and guidelines that
often seems to go against the conventional wisdom. On other occasions, XP just
seems to emphasize the common sense, which doesn't always coincide with common
practice. For example, XP stresses the importance of normal workweeks, if we are
to have the fresh mind needed for good software development.

.. % 

It is not my intention nor qualification to present a tutorial on Extreme
Programming. Instead, in this section I will highlight one XP concept which I
think is very relevant to hardware design: the importance and methodology of
unit testing.


.. _unittest-why:

The importance of unit tests
============================

Unit testing is one of the corner stones of Extreme Programming. Other XP
concepts, such as collective ownership of code and continuous refinement, are
only possible by having unit tests. Moreover, XP emphasizes that writing unit
tests should be automated, that they should test everything in every class, and
that they should run perfectly all the time.

I believe that these concepts apply directly to hardware design. In addition,
unit tests are a way to manage simulation time. For example, a state machine
that runs very slowly on infrequent events may be impossible to verify at the
system level, even on the fastest simulator. On the other hand, it may be easy
to verify it exhaustively in a unit test, even on the slowest simulator.

It is clear that unit tests have compelling advantages. On the other hand, if we
need to test everything, we have to write lots of unit tests. So it should be
easy and pleasant to create, manage and run them. Therefore, XP emphasizes the
need for a unit test framework that supports these tasks. In this chapter, we
will explore the use of the ``unittest`` module from the standard Python library
for creating unit tests for hardware designs.


.. _unittest-dev:

Unit test development
=====================

In this section, we will informally explore the application of unit test
techniques to hardware design. We will do so by a (small) example: testing a
binary to Gray encoder as introduced in section :ref:`intro-indexing`.


.. _unittest-req:

Defining the requirements
-------------------------

We start by defining the requirements. For a Gray encoder, we want to the output
to comply with Gray code characteristics. Let's define a :dfn:`code` as a list
of :dfn:`codewords`, where a codeword is a bit string. A code of order ``n`` has
``2**n`` codewords.

A well-known characteristic is the one that Gray codes are all about:

Consecutive codewords in a Gray code should differ in a single bit.

Is this sufficient? Not quite: suppose for example that an implementation
returns the lsb of each binary input. This would comply with the requirement,
but is obviously not what we want. Also, we don't want the bit width of Gray
codewords to exceed the bit width of the binary codewords.

Each codeword in a Gray code of order n must occur exactly once in the binary
code of the same order.

With the requirements written down we can proceed.


.. _unittest-first:

Writing the test first
----------------------

A fascinating guideline in the XP world is to write the unit test first. That
is, before implementing something, first write the test that will verify it.
This seems to go against our natural inclination, and certainly against common
practices. Many engineers like to implement first and think about verification
afterwards.

But if you think about it, it makes a lot of sense to deal with verification
first. Verification is about the requirements only --- so your thoughts are not
yet cluttered with implementation details. The unit tests are an executable
description of the requirements, so they will be better understood and it will
be very clear what needs to be done. Consequently, the implementation should go
smoother. Perhaps most importantly, the test is available when you are done
implementing, and can be run anytime by anybody to verify changes.

Python has a standard ``unittest`` module that facilitates writing, managing and
running unit tests. With ``unittest``, a test case is  written by creating a
class that inherits from ``unittest.TestCase``. Individual tests are created by
methods of that class: all method names that start with ``test`` are considered
to be tests of the test case.

We will define a test case for the Gray code properties, and then write a test
for each of the requirements. The outline of the test case class is as follows::

   from unittest import TestCase

   class TestGrayCodeProperties(TestCase):

       def testSingleBitChange(self):
        """ Check that only one bit changes in successive codewords """
        ....


       def testUniqueCodeWords(self):
           """ Check that all codewords occur exactly once """
       ....

Each method will be a small test bench that tests a single requirement. To write
the tests, we don't need an implementation of the Gray encoder, but we do need
the interface of the design. We can specify this by a dummy implementation, as
follows::

   def bin2gray(B, G, width):
       ### NOT IMPLEMENTED YET! ###
       yield None

For the first requirement, we will write a test bench that applies all
consecutive input numbers, and compares the current output with the previous one
for each input. Then we check that the difference is a single bit. We will test
all Gray codes up to a certain order ``MAX_WIDTH``. ::

   def testSingleBitChange(self):
       """ Check that only one bit changes in successive codewords """

       def test(B, G, width):
           B.next = intbv(0)
           yield delay(10)
           for i in range(1, 2**width):
               G_Z.next = G
               B.next = intbv(i)
               yield delay(10)
               diffcode = bin(G ^ G_Z)
               self.assertEqual(diffcode.count('1'), 1)

       for width in range(1, MAX_WIDTH):
           B = Signal(intbv(-1))
           G = Signal(intbv(0))
           G_Z = Signal(intbv(0))
           dut = bin2gray(B, G, width)
           check = test(B, G, width)
           sim = Simulation(dut, check)
           sim.run(quiet=1)

Note how the actual check is performed by a ``self.assertEqual`` method, defined
by the ``unittest.TestCase`` class.

Similarly, we write a test bench for the second requirement. Again, we simulate
all numbers, and put the result in a list. The requirement implies that if we
sort the result list, we should get a range of numbers::

   def testUniqueCodeWords(self):
       """ Check that all codewords occur exactly once """

       def test(B, G, width):
           actual = []
           for i in range(2**width):
               B.next = intbv(i)
               yield delay(10)
               actual.append(int(G))
           actual.sort()
           expected = range(2**width)
           self.assertEqual(actual, expected)

       for width in range(1, MAX_WIDTH):
           B = Signal(intbv(-1))
           G = Signal(intbv(0))
           dut = bin2gray(B, G, width)
           check = test(B, G, width)
           sim = Simulation(dut, check)
           sim.run(quiet=1)


.. _unittest-impl:

Test-driven implementation
--------------------------

With the test written, we begin with the implementation. For illustration
purposes, we will intentionally write some incorrect implementations to see how
the test behaves.

The easiest way to run tests defined with the ``unittest`` framework, is to put
a call to its ``main`` method at the end of the test module::

   unittest.main()

Let's run the test using the dummy Gray encoder shown earlier::

   % python test_gray.py -v
   Check that only one bit changes in successive codewords ... FAIL
   Check that all codewords occur exactly once ... FAIL
   <trace backs not shown>

As expected, this fails completely. Let us try an incorrect implementation, that
puts the lsb of in the input on the output::

   def bin2gray(B, G, width):
       ### INCORRECT - DEMO PURPOSE ONLY! ###

       @always_comb
       def logic():
           G.next = B[0]

       return logic

Running the test produces::

   % python test_gray.py -v
   Check that only one bit changes in successive codewords ... ok
   Check that all codewords occur exactly once ... FAIL

   ======================================================================
   FAIL: Check that all codewords occur exactly once
   ----------------------------------------------------------------------
   Traceback (most recent call last):
     File "test_gray.py", line 109, in testUniqueCodeWords
       sim.run(quiet=1)
   ...
     File "test_gray.py", line 104, in test
       self.assertEqual(actual, expected)
     File "/usr/local/lib/python2.2/unittest.py", line 286, in failUnlessEqual
       raise self.failureException, \
   AssertionError: [0, 0, 1, 1] != [0, 1, 2, 3]

   ----------------------------------------------------------------------
   Ran 2 tests in 0.785s

Now the test passes the first requirement, as expected, but fails the second
one. After the test feedback, a full traceback is shown that can help to debug
the test output.

Finally, if we use the correct implementation as in section
:ref:`intro-indexing`, the output is::

   % python test_gray.py -v
   Check that only one bit changes in successive codewords ... ok
   Check that all codewords occur exactly once ... ok

   ----------------------------------------------------------------------
   Ran 2 tests in 6.364s

   OK


.. _unittest-change:

Changing requirements
---------------------

In the previous section, we concentrated on the general requirements of a Gray
code. It is possible to specify these without specifying the actual code. It is
easy to see that there are several codes that satisfy these requirements. In
good XP style, we only tested the requirements and nothing more.

It may be that more control is needed. For example, the requirement may be for a
particular code, instead of compliance with general properties. As an
illustration, we will show how to test for *the* original Gray code, which is
one specific instance that satisfies the requirements of the previous section.
In this particular case, this test will actually be easier than the previous
one.

We denote the original Gray code of order ``n`` as ``Ln``. Some examples::

   L1 = ['0', '1']
   L2 = ['00', '01', '11', '10']
   L3 = ['000', '001', '011', '010', '110', '111', '101', 100']

It is possible to specify these codes by a recursive algorithm, as follows:

#. L1 = ['0', '1']

#. Ln+1 can be obtained from Ln as follows. Create a new code Ln0 by prefixing
   all codewords of Ln with '0'. Create another new code Ln1 by prefixing all
   codewords of Ln with '1', and reversing their order. Ln+1 is the concatenation
   of Ln0 and Ln1.

Python is well-known for its elegant algorithmic descriptions, and this is a
good example. We can write the algorithm in Python as follows::

   def nextLn(Ln):
       """ Return Gray code Ln+1, given Ln. """
       Ln0 = ['0' + codeword for codeword in Ln]
       Ln1 = ['1' + codeword for codeword in Ln]
       Ln1.reverse()
       return Ln0 + Ln1

The code ``['0' + codeword for ...]`` is called a :dfn:`list comprehension`. It
is a concise way to describe lists built by short computations in a for loop.

The requirement is now that the output code matches the expected code Ln. We use
the ``nextLn`` function to compute the expected result. The new test case code
is as follows::

   class TestOriginalGrayCode(TestCase):

       def testOriginalGrayCode(self):
           """ Check that the code is an original Gray code """

           Rn = []

           def stimulus(B, G, n):
               for i in range(2**n):
                   B.next = intbv(i)
                   yield delay(10)
                   Rn.append(bin(G, width=n))

           Ln = ['0', '1'] # n == 1
           for n in range(2, MAX_WIDTH):
               Ln = nextLn(Ln)
               del Rn[:]
               B = Signal(intbv(-1))
               G = Signal(intbv(0))
               dut = bin2gray(B, G, n)
               stim = stimulus(B, G, n)
               sim = Simulation(dut, stim)
               sim.run(quiet=1)
               self.assertEqual(Ln, Rn)

As it happens, our implementation is apparently an original Gray code::

   % python test_gray.py -v TestOriginalGrayCode
   Check that the code is an original Gray code ... ok

   ----------------------------------------------------------------------
   Ran 1 tests in 3.091s

   OK

