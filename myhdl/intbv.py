""" Module with intbv class """

import sys
maxint = sys.maxint
from types import StringType

   

class intbv(object):
    __slots__ = ('_val', '_len')
    
    def __init__(self, val=0):
        self._len = 0
        if type(val) is intbv:
            self._val = val._val
        elif type(val) is StringType:
            self._val = long(val, 2)
            self._len = len(val)
        else:
            self._val = val

    # concat method
    def concat(self, *args):
        val = self._val
        basewidth = width = 0
        if type(val) is intbv:
            v = val._val
            basewidth = width = val._len
        else:
            v = val
        for a in args:
            if type(a) is intbv:
                w = a._len
                if not w:
                    raise TypeError, "intbv arg to concat should have length"
                else:
                    v = v * (2**w) + a._val
                    width += w
            elif type(a) is StringType:
                w = len(a)
                v= v*(2**w) + long(a, 2)
                width += w
            else:
                raise TypeError
        try:
            v = int(v)
        except:
            pass
        res = intbv(v)
        if basewidth:
            res._len = basewidth + width
        return res

    # copy methods
    def __copy__(self):
        return intbv(self._val)
    def __deepcopy__(self, visit):
        return intbv(self._val)

    # logical testing
    def __nonzero__(self):
        if self._val:
            return 1
        else:
            return 0

    # indexing and slicing methods

    def __getitem__(self, i):
        res = intbv((self._val >> i) & 0x1)
        res._len = 1
        return res

    def __getslice__(self, i, j):
        if j == maxint: # default if not supplied
            j = 0
        if i <= j or i < 1 or j < 0:
            raise ValueError, "intbv[i:j]: requires i > j >= 0"
        res = intbv((self._val & 2**i-1) >> j)
        res._len = i-j
        return res
        
    def __setitem__(self, i, v):
        val = v
        if type(val) is intbv:
            val = v._val
        if val not in (0, 1):
            raise ValueError, "intbv[i] = v: requires v in (0, 1)"
        if val:
            self._val |= (2**i)
        else:
            self._val &= ~(2**i)

    def __setslice__(self, i, j, v):
        if j == maxint: # default if not supplied
            j = 0
        val = v
        if type(val) is intbv:
            val = v
        if i <= j or i < 1 or j < 0:
            raise ValueError, "intbv[i:j] = v: requires i > j >= 0"
        if val >= 2**(i-j):
            raise ValueError, "intbv[i:j] = v: v too large"
        mask = (2**(i-j))-1
        mask *= 2**j
        self._val &= ~mask
        self._val |= val * 2**j
              
        
    # integer-like methods
    
    def __add__(self, other):
        if type(other) is intbv:
            return intbv(self._val + other._val)
        else:
            return intbv(self._val + other)
    def __radd__(self, other):
        return intbv(other + self._val)
    
    def __sub__(self, other):
        if type(other) is intbv:
            return intbv(self._val - other._val)
        else:
            return intbv(self._val - other)
    def __rsub__(self, other):
        return intbv(other - self._val)

    def __mul__(self, other):
        if type(other) is intbv:
            return intbv(self._val * other._val)
        else:
            return intbv(self._val * other)
    def __rmul__(self, other):
        return intbv(other * self._val)

    def __div__(self, other):
        if type(other) is intbv:
            return intbv(self._val / other._val)
        else:
            return intbv(self._val / other)
    def __rdiv__(self, other):
        return intbv(other / self._val)
    
    def __mod__(self, other):
        if type(other) is intbv:
            return intbv(self._val % other._val)
        else:
            return intbv(self._val % other)
    def __rmod__(self, other):
        return intbv(other % self._val)

    # divmod
    
    def __pow__(self, other):
        if type(other) is intbv:
            return intbv(self._val ** other._val)
        else:
            return intbv(self._val ** other)
    def __rpow__(self, other):
        return intbv(other ** self._val)

    def __lshift__(self, other):
        if type(other) is intbv:
            return intbv(self._val << other._val)
        else:
            return intbv(self._val << other)
    def __rlshift__(self, other):
        return intbv(other << self._val)
            
    def __rshift__(self, other):
        if type(other) is intbv:
            return intbv(self._val >> other._val)
        else:
            return intbv(self._val >> other)
    def __rrshift__(self, other):
        return intbv(other >> self._val)
           
    def __and__(self, other):
        if type(other) is intbv:
            return intbv(self._val & other._val)
        else:
            return intbv(self._val & other)
    def __rand__(self, other):
        return intbv(other & self._val)

    def __or__(self, other):
        if type(other) is intbv:
            return intbv(self._val | other._val)
        else:
            return intbv(self._val | other)
    def __ror__(self, other):
        return intbv(other | self._val)
    
    def __xor__(self, other):
        if type(other) is intbv:
            return intbv(self._val ^ other._val)
        else:
            return intbv(self._val ^ other)
    def __rxor__(self, other):
        return intbv(other ^ self._val)

    def __iadd__(self, other):
        if type(other) is intbv:
            self._val += other._val
        else:
            self._val += other
        return self
        
    def __isub__(self, other):
        if type(other) is intbv:
            self._val -= other._val
        else:
            self._val -= other
        return self
        
    def __imul__(self, other):
        if type(other) is intbv:
            self._val *= other._val
        else:
            self._val *= other
        return self
        
    def __idiv__(self, other):
        if type(other) is intbv:
            self._val /= other._val
        else:
            self._val /= other
        return self
    
    def __imod__(self, other):
        if type(other) is intbv:
            self._val %= other._val
        else:
            self._val %= other
        return self
        
    def __ipow__(self, other, modulo): # XXX why 3rd param required?
        if type(other) is intbv:
            self._val **= other._val
        else:
            self._val **= other
        return self
        
    def __iand__(self, other):
        if type(other) is intbv:
            self._val &= other._val
        else:
            self._val &= other
        return self

    def __ior__(self, other):
        if type(other) is intbv:
            self._val |= other._val
        else:
            self._val |= other
        return self

    def __ixor__(self, other):
        if type(other) is intbv:
            self._val ^= other._val
        else:
            self._val ^= other
        return self

    def __ilshift__(self, other):
        if type(other) is intbv:
            self._val <<= other._val
        else:
            self._val <<= other
        return self

    def __irshift__(self, other):
        if type(other) is intbv:
            self._val >>= other._val
        else:
            self._val >>= other
        return self

    def __neg__(self):
        return intbv(-self._val)

    def __pos__(self):
        return intbv(+self._val)

    def __abs__(self):
        return intbv(abs(self._val))

    def __invert__(self):
        if self._len:
            return intbv(~self._val & (2**self._len)-1)
        else:
            return intbv(~self._val)
    
    def __int__(self):
        return int(self._val)
        
    def __long__(self):
        return long(self._val)

    def __float__(self):
        return float(self._val)

    # XXX __complex__ seems redundant ??? (complex() works as such?)
    
    def __oct__(self):
        return oct(self._val)
    
    def __hex__(self):
        return hex(self._val)
      
    def __repr__(self):
        return repr(self._val)
        
    def __cmp__(self, other):
        if type(other) is intbv:
            return cmp(self._val, other._val)
        else:
            return cmp(self._val, other)

