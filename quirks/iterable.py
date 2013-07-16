
from itertools import *

def isiterable(obj):
    from collections import Iterable
    return isinstance(obj, Iterable)


def itake(n, it):
    from itertools import izip,imap,count,takewhile
    return imap(lambda x:x[1],takewhile(lambda x:x[0]<n, izip(count(),it)))    


def first(iterable):
    return iter(iterable).next() if iterable else None

class ensure_iterable(object):
    def __init__(self, function):
        self.function = function
    def __call__(self, *args, **kwargs):
        result = self.function(*args, **kwargs)
        return result if isiterable(result) else (result,)

