import copy_reg
import types



##################################
class BoidBaseObject(object):
    """Base class for all the other boid classes in this package.  Treated as an abstract class, I
    suppose (although, technically, it isn't one).
    Raison d'etre just to kind of formalise the 'metaStr' implementation...
    
    Throughout the classes in this package, metaStr is used as a complement to the usual
    __str__ method for giving detailed info on the more 'meta' attributes.  
    It's purely for logging and debugging.
    """
    
    def _getMetaStr(self):
        """Override to provide a seperate output for self.metaStr property"""
        return ("<_getMetaStr has not been implemented for type %s>" % type(self))
    metaStr = property(lambda obj:obj._getMetaStr())  # the lambda complication is necessary to make this property
    #                                                 # accessor work correctly with the inheritance heirarchy.
    
###########################
    def __getstate__(self):
        """Subclasses that need to save internal state during a save operation should 
        override this method and the corresponding __setstate__ method if:
        - any member variables are pointers to lambda methods
        - any member variables are weak references.
        In either of these two situations, the offending objects must be removed from
        the returned dictionary in __getstate__ (placemarker objects can be put in place).
        The objects should be restored or recreated in the __setstate__ method if necessary. 
        See the Python docs on Pickle for more info.
        """
        return self.__dict__.copy()
    
    def __setstate__(self, state):
        """Subclasses that need to save internal state during a save operation should 
        override this method and the corresponding __getstate__ method if:
        - any member variables are pointers to lambda methods
        - any member variables are weak references.
        In either of these two situations, the offending objects must be removed from
        the returned dictionary in __getstate__ (placemarker objects can be put in place).
        The objects should be restored or recreated in the __setstate__ method. 
        See the Python docs on Pickle for more info.
        """
        self.__dict__.update(state)
    
# END OF CLASS - BoidBaseObject
####################################



####################################
# The below code replaces the default Pickle
# algorithm for pickling methods.  It is
# a workaround for one of Pickel's 
# shortcomings - the fact that, out of the
# box, Pickle is not able to handle the
# serialisation of object instance attributes
# which point to bound methods.

_lambdaName = (lambda: None).__name__

################
def _PickleMethod(methodInstance):
    functionName = methodInstance.im_func.__name__
        
    obj = methodInstance.im_self
    cls = methodInstance.im_class
    
    if(functionName == _lambdaName):
        raise ValueError("Found bound lambda method %s (object=%s, type=%s), which is not compatable with the save mechanism.  \
Recommended you remove & restore this in object's __getstate__ and __setstate__ methods" % (functionName, obj, cls))
        
    return (_UnpickleMethod, (functionName, obj, cls))

################
def _UnpickleMethod(functionName, obj, cls):
    for clsCandidate in cls.mro():
        try:
            function = clsCandidate.__dict__[functionName]
        except KeyError:
            pass
        else:
            break
    return function.__get__(obj, cls)

################
copy_reg.pickle(types.MethodType, _PickleMethod, _UnpickleMethod)

