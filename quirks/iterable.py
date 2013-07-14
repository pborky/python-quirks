
from itertools import *

def isiterable(obj):
    from collections import Iterable
    return isinstance(obj, Iterable)


def itake(n, it):
    from itertools import izip,imap,count,takewhile
    return imap(lambda x:x[1],takewhile(lambda x:x[0]<n, izip(count(),it)))    
