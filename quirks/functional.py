from operator import *
from math import *
from functools import *


def combinator(*fncs):
    return lambda *args:getitem(
            reduce(lambda acc,fnc:(fnc(*acc),), 
                   reversed(fncs), 
                   args), 0)

def flip(f):
    return lambda *a: f(*reversed(a))

class maybe(object):
    """inspired by haskell's Maybe monad"""
    def __init__(self, *functions):
        self.functions = functions
    def __call__(self, *args, **kwargs):
        for fnc in self.functions:
            try:
                res = fnc(*args, **kwargs)
            except:
                res = None
            if res is not None:
                return res
        return None

# example of usage (overkill little-bit?:)
def minkowski(n, p1, p2):
    from itertools import imap
    rpow = flip(pow)
    nth_pow = partial(rpow,n)
    nth_root = partial(rpow,1./n)
    return nth_root(reduce(add, imap(combinator(nth_pow,sub),p1,p2)))

euclid = partial(minkowski,2)
