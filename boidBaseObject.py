import boidTools.util as util

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
    
# END OF CLASS - BoidBaseObject
####################################



####################################
_lambdaName = (lambda: None).__name__

################
def _PickleMethod(methodInstance):
    functionName = methodInstance.im_func.__name__
        
    obj = methodInstance.im_self
    cls = methodInstance.im_class
    
    if(functionName == _lambdaName):
        util.LogWarning("Found bound lambda method %s (object=%s, type=%s), which is not compatable with the save mechanism.  \
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

