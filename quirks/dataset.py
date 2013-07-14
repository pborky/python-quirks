"""Classes encapsulating HDF5 files and numpy matrices.

"""

from util import *

class H5Node(object):
    """Creates group in H5 file.
    Opens h5 file if not provided in argument 'h5'.

    Parameters
    ----------
    opt : argparse.Namespace
        Arguements passed in command line.
    h5 : tables.File
        An instance of H5 file
    grp : tables.Group
        An instance of H5 group
    auto_create_grps : boolean
        if True ne group is created if it is non-existent

    """
    def __init__(self, opt, h5 = None, grp = None, auto_create_grps = True ):
        from tables import openFile,File
        if isinstance(h5,File):
            self.h5 = h5
        else:
            db = opt if isinstance(opt,str) else  opt.database
            self.h5 = openFile(db,'a')
        self.group = self.h5.root if grp is None else grp
        self.opt = opt
        self.auto_create_grps = auto_create_grps
    def _keyfnc(self,g):
        return g._v_pathname.rsplit('/',1)[-1]
    def _itemfnc(self,g):
        return self._keyfnc(g),self._get_item(g)
    def __len__(self):
        return len(self.keys())
    def __iter__(self):
        from itertools import imap
        return imap(self._keyfnc,self.h5.iterNodes(self.group))
    def __reversed__(self):
        return reversed(self.keys())
    def iteritems(self):
        from itertools import imap
        return imap(self._itemfnc,self.h5.iterNodes(self.group))
    def has_key(self,key):
        return key in self
    def iterkeys(self):
        return iter(self)
    def itervalues(self):
        from itertools import imap
        return imap(self._get_item,self.h5.iterNodes(self.group))
    def keys(self):
        return  [ i for i in iter(self) ]
    def values(self):
        return  [ v for v in self.itervalues() ]
    def items(self):
        return  [ i for i in self.iteritems() ]
    def get(self,key,d=None):
        return self[key] if key in self else d
    def __contains__(self, item):
        from tables import NoSuchNodeError
        try:
            self.h5.getNode(self.group,item)
            return True
        except NoSuchNodeError:
            return False
    def __delitem__(self, key):
        self.h5.getNode(self.group,key)._f_remove(True)
    def _get_item(self,item):
        from tables import Node,Group
        if isinstance(item,Node):
            if isinstance(item,Group):
                result = H5Node(self.opt,h5=self.h5, grp=item)
                if 'data' in result and 'fields' in result:
                    return Table(h5=result)
                else:
                    return result
            else:
                return scalar(item)

    def _get_current_path(self):
        if self._is_root():
            return '/'
        else:
            return self.group._v_pathname.rstrip('/')

    def _is_root(self):
        return self.group._v_pathname  == '/'

    def _get_absolute_path(self,key):
        if key[0] == '/' and not self._is_root():
            raise ValueError("the ``/`` character is not allowed in object names of non-root group: '%s'"%key)
        path = key.rsplit('/',1)
        if len(path)==2:
            path,name = path
            if self._is_root():
                path =  '/' + path.lstrip('/')
            else:
                path = self._get_current_path() +'/' + path
        else:
            name, = path
            path = self._get_current_path()
        return  path,name

    def __getitem__(self, item):
        from tables import Node,NoSuchNodeError

        if isinstance(item,Node):
            return self._get_item(item)
        else:
            path,name = self._get_absolute_path(item)
            try:
                item = self.h5.getNode(path,name)
            except NoSuchNodeError:
                if not self.auto_create_grps:
                    raise
                item =  self.h5.createGroup(path,name,createparents=True)
            return self._get_item(item)
    def __setitem__(self, key, value):
        path,name = self._get_absolute_path(key)
        if not isSequenceType(value):
            value = value,
        self.h5.createArray(path,name,value, createparents=True)
    def close(self):
        self.h5.close()
    def handle_exit(self, try_fnc, *arg,**kwarg):
        """Call 'try_fnc(opt,h5=h5)' in try-finally block. At the end close the file and exit.

        """
        if not callable(try_fnc):
            raise ValueError()
        try:
            try_fnc(self.opt, h5 = self)
        except KeyboardInterrupt:
            pass
        finally:
            self.close()
        exit()
    def _printNode(self, key, val, padding= '', last=False,maxdepth=None,maxcount=None):
        from fabulous.color import highlight_blue,red,blue,green,cyan,yellow,bold
        from tables import Array

        if isinstance(val,H5Node):
            val.printTree(padding=padding,last=last,maxdepth=maxdepth,maxcount=maxcount)
        else:
            if isinstance(val,Array):
                val = yellow('Array(%s,__dtype__=%s)'% (','.join(str(i) for i in val.shape),val.dtype))
            elif isinstance(val,Table):
                val = green(val)
            else:
                val = red('%s,__dtype__=%s' % (str(val),type(val).__name__))
            if last:
                print '%s `%s [%s]' % (padding[:-1], cyan(key), val )
            else:
                print '%s`%s [%s]' % (padding, cyan(key), val )

    def printTree(self, padding= '', last=False,maxdepth=3,maxcount=50):
        """Print tree contained in file.

        Parameters
        ----------
        padding : string
            Arguements passed in command line.
        last : boolean
            Last node in sequence
        maxdepth : number
            Limit dept
        maxcount : number
            Limit count

        """

        if maxdepth is not None and maxdepth<0:
            print padding[:-1] + ' `'+bold(blue('...'))
            return

        if last:
            print padding[:-1] + ' `' + bold(blue(self._keyfnc(self.group) + '/' ))
            padding = padding[:-1]+' '
        else:
            print padding + '`' + bold(blue(self._keyfnc(self.group) + '/')  )

        count = len(self)
        large = False
        if maxcount is not None and count>maxcount:
            count=maxcount+1
            large = True
        if self is None or not count:
            print padding, ' `'+boldblack('[empty]')
        else:
            for key, val in self.iteritems():
                count -= 1
                if count==0 and large:
                    #print padding + ' |-'+(cyan('(...)'))
                    print padding + ' '+'`...'
                    break
                self._printNode(key,val,padding=padding+' |',last=not count,maxdepth=maxdepth-1,maxcount=maxcount)

class Table(object):
    """Encapsulation of the numpy array, in order to conviently select/update data
    .
    Parameters
    ----------
    data : array-like [n_rows, len(fields)]
        the data representing this table
    fields : tuple
        tuple of strings representing columns
    h5 : dataset.H5Node
        Initialize Table from HDF5 file
    """
    def __init__(self, data=None, fields=None, h5=None):
        from numpy import array,ndarray
        if h5 is not None:
            self.h5 = h5
            self.data = h5['data'][...]
            self.fields = tuple(h5['fields'])
        elif data is not None and fields is not None:
            self.data = data if isinstance(data,ndarray) else array(data)
            self.fields = tuple(fields)
        else:
            raise Exception('no data')
        for f in self.fields:
            setattr(self,f,Variable(f))
    def __add__(self,other):
        """add two dataset objects. Must have same shape and fields."""
        from numpy import vstack
        if not isinstance(other,Table):
            raise TypeError('Must be Dataset')
        if self.fields != other.fields:
            raise TypeError('Must have same fields')
        if not len(self):
            return Table(data=other.data,fields=self.fields)
        elif not len(other):
            return self
        else:
            return Table(data=vstack((self.data,other.data)),fields=self.fields)
    def __len__(self):
        """return the length of the dataset."""
        return self.data.shape[0]
    def _check_fields(self,fields):
        err = [f for f in fields if f not in self.fields]
        if len(err):
            raise ValueError('some fields not in this dataset (%s)' % err)
    def _parse_key(self,key):
        if isinstance(key, tuple):
            if isinstance(key[0],(int,slice,Predicate)) or key[0] is Ellipsis:
                pred,fields,retdset = key[0],key[1:],True
            else:
                pred,fields,retdset =  None,key,False
        elif isinstance(key,(int,slice,Predicate)) or key is Ellipsis:
            pred,fields,retdset =  key,None,True
        else:
            pred,fields,retdset =  None,(key,),False

        if isinstance(fields,tuple) and len(fields) == 1 and isinstance(fields[0],slice):
            self._check_fields((fields[0].start,fields[0].stop))
        elif fields is not None:
            self._check_fields(fields)
        return pred,fields,retdset
    def __getitem__(self, key):
        pred,fields,retdset = self._parse_key(key)
        return self.select(pred,fields=fields,retdset=retdset)
    def __delitem__(self, key):
        pred,fields,retdset = self._parse_key(key)
        d = self.select(pred,fields=fields,retdset=retdset)
        self.data,self.fields = d.data,d.fields
    def __setitem__(self, key, value):
        if not len(self):
            return
        pred,fields,retdset = self._parse_key(key)
        return self.set_fields(pred, fields, value)
    def __contains__(self,item):
        return item in self.fields
    def __iter__(self):
        return ( self[i] for i in xrange(len(self)) )
    def keys(self):
        return self.fields
    def __str__(self):
        return 'Table(%s,__len__=%d,__dtype__=%s)'%( ','.join(self.keys()), len(self),self.data.dtype)
    def __repr__(self):
        return '<dataset.Table(%s,__len__=%d,__dtype__=%s)>'%( ','.join(self.keys()), len(self),self.data.dtype)
    def _getfield(self,x,f):
        """return vector containing the field"""
        return x[...,self.fields.index(f)]
    def _get_indexing(self,predicate,fields):
        from numpy import array,newaxis,ndarray
        # rows
        if callable(predicate):
            pred = predicate (self.data, self._getfield)
        elif isinstance(predicate,int):
            pred =  slice(predicate,predicate+1)
        elif isinstance(predicate, slice) or predicate is Ellipsis:
            pred =  predicate
        else:
            pred = Ellipsis
        # columns
        if isinstance(fields,tuple) and len(fields) == 1 :
            if isinstance(fields[0],slice):
                fldidx = slice(self.fields.index(fields[0].start),self.fields.index(fields[0].stop))
            else:
                fldidx = self.fields.index(fields[0])
                fldidx = slice(fldidx,fldidx+1)
            fields = self.fields[fldidx]
        elif fields:
            fldidx = array([ f in fields for f in self.fields ])
        else:
            fields = self.fields
            fldidx = Ellipsis

        return (pred,fldidx),fields
    def squeeze(self):
        return self.data.squeeze()
    def select(self, predicate, order=None, retdset=None, fields=None, **kwargs):
        """Select submatrix based on predicate and fields.

        Example:
            size = PredicateFactory('size')
            r = data.select((size >= 10) & (size < 15), fields = ('time', 'size'))
            # select submatrix containing time and size columns and rows where size is in interval [10,15)

        Parameters
        ----------
        predicate : dataset.Predicate
            Vector predicate to use for an indexing.
        order : string
            Determine field to be used for ordering of the result.
        retdset : boolean
            If true result is wrapped in new dataset.Table instance.
        fields : tuple
            Fields to retain in result.


        Returns
        -------
            a submatrix or a new Table object based on predicate
        """
        from numpy import argsort,ndarray

        idx,fields = self._get_indexing(predicate,fields)
        if isinstance(idx[0],ndarray) and isinstance(idx[1],ndarray):
            result = self.data[idx[0],...][...,idx[1]]
        else:
            result = self.data[idx]

        if order is not None and order in fields:
            result = result[argsort( result[...,self.fields.index(order)] ),...]
        if retdset:
            return Table(data=result,fields=fields)
        else:
            return result
    def add_field(self, field, default):
        """Add new column called 'field' and set its value to 'default'. It can be vector or scalar (it will be broadcast)."""
        from numpy import hstack,ndarray
        buff = ndarray( shape=(self.data.shape[0],1),dtype=self.data.dtype)
        buff[:] = default
        self.data,self.fields = hstack((self.data,buff)),self.fields+(field,)
    def retain_fields(self, fields):
        """Keep column specified in 'fields', others are discarded."""
        if any(f not in self.fields for f in fields):
            raise ValueError('some fields not in this dataset')
        self.data = self.data[...,tuple(self.fields.index(f) for f in fields)]
        self.fields = fields
    def set_fields(self, predicate, fields, value):
        """Set column specified by 'field', and rows matched by 'predicate' set its value to 'value'.
           It can be vector or scalar (it will be broadcast).
        """
        from numpy import ndarray

        idx,fields = self._get_indexing(predicate,fields)
        # evaluate
        if callable(value):
            self.data[idx] = value(self.data[idx])
        else:
            self.data[idx] = value

        # return updated row count

        return idx.shape[0] if isinstance(idx,ndarray) else idx[0].shape[0] if isinstance(idx[0],ndarray) else -1

    def save(self,h5):
        """Save the content in 'h5' group.


        Parameters
        ----------
        h5 : H5Node
            a node to store the content

        """
        h5['data'] =  self.data
        h5['fields'] =  self.fields

## convivence method for compsoting coditions.
class Predicate(object):
    def __call__(self,arg, fnc):
        raise Exception('not implementd')
    def __and__(self, other):
        return Conj(self,other)
    def __or__(self, other):
        return Dis(self,other)
    def __xor__(self, other):
        return Xor(self,other)
    def __eq__(self, other):
        return Equ(self,other)

class Term(Predicate):
    def __init__(self, field,value):
        self.value = value
        self.field = field
class Always(Term):
    def __call__(self, arg, fnc):
        a = fnc(arg,self.field)
        return a==a
class Never(Term):
    def __call__(self, arg, fnc):
        a = fnc(arg,self.field)
        return a!=a
class Lt(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) < self.value
class Gt(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) > self.value
class Le(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) <= self.value
class Ge(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) >= self.value
class Eq(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) == self.value
class Ne(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) != self.value
class And(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) & self.value
class Or(Term):
    def __call__(self,arg, fnc):
        return fnc(arg,self.field) | self.value
class In(Term):
    def __call__(self,arg, fnc):
        from operator import or_
        d = fnc(arg,self.field) if callable(fnc) else fnc
        return reduce(or_, (i==d for i in self.value))

class Binary(Predicate):
    def __init__(self, reduction, *args):
        super(Binary, self).__init__()
        argsg = (a.preds if isinstance(a,self.__class__) else (a,) for a in args)
        self.preds = tuple(i for sub in argsg for i in sub)
        self.reduction = reduction if reduction else tuple
    def __call__(self, arg, fnc):
        return reduce(self.reduction, (p(arg,fnc) if callable(p) else p for p in self.preds))
class Conj(Binary):
    def __init__(self, *args):
        from operator import and_
        super(Conj, self).__init__(and_,*args)
class Dis(Binary):
    def __init__(self, *args):
        from operator import or_
        super(Dis, self).__init__(or_,*args)
class Xor(Binary):
    def __init__(self, *args):
        from operator import xor
        super(Xor, self).__init__(xor,*args)
class Equ(Binary):
    def __init__(self, *args):
        from operator import eq
        super(Equ, self).__init__(eq,*args)

class Variable(object):
    """Factory object to build an predicate instances.

    Parameters
    ----------
    field : string
        a name of the variable

    """
    def __init__(self, field):
        self.field = field
    def __lt__(self,other):
        return Lt(self.field,other)
    def __gt__(self,other):
        return Gt(self.field,other)
    def __eq__(self,other):
        return Eq(self.field,other)
    def __ne__(self,other):
        return Ne(self.field,other)
    def __le__(self,other):
        return Le(self.field,other)
    def __ge__(self,other):
        return Ge(self.field,other)
    def __contains__(self,other):
        return In(self.field, other)
    def __and__(self, other):
        return And(self.field, other)
    def __or__(self, other):
        return Or(self.field, other)
    def always(self):
        return Always(self.field,None)
    def never(self):
        return Never(self.field,None)
    def nonzero(self):
        return Nz(self.field)
