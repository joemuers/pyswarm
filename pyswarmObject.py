#
# PySwarm, a swarming simulation tool for Autodesk Maya
#
# created 2013-2014
#
# @author: Joe Muers  (joemuers@hotmail.com)
# 
# All rights reserved.
#
# ------------------------------------------------------------


import copy_reg
import types



##################################
class PyswarmObject(object):
    """
    Base class for all the other PySwarm classes in this package.  Treated as an abstract class, I
    suppose (although, technically, it isn't one).
    Raison d'etre just to kind of formalise the 'debugStr' implementation...
    
    Throughout the classes in this package, the debugStr property is used as a complement to the usual
    __str__ method for giving more detailed info on it's attributes.  
    It's purely for logging and debugging.
    """
    
    def _getDebugStr(self):
        """
        Override to provide a seperate output for self.debugStr property
        """
        return ("<_getDebugStr has not been implemented for type %s>" % type(self))
    debugStr = property(lambda obj:obj._getDebugStr())  # the lambda complication is necessary to make this property
    #                                                   # accessor work correctly with the inheritance heirarchy.
    
###########################
    def __getstate__(self):
        """
        Subclasses that need to save internal state during a save operation should 
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
        """
        Subclasses that need to save internal state during a save operation should 
        override this method and the corresponding __getstate__ method if:
        - any member variables are pointers to lambda methods
        - any member variables are weak references.
        
        In either of these two situations, the offending objects must be removed from
        the returned dictionary in __getstate__ (placemarker objects can be put in place).
        The objects should be restored or recreated in the __setstate__ method. 
        
        See the Python docs on Pickle for more info.
        """
        self.__dict__.update(state)
    
# END OF CLASS - PyswarmObject
####################################



# Pickle is used in this package to save the state of PySwarm to disk. The below is a workaround to tackle 
# one of Pickle's shortcomings - that is cannot Pickle bound methods.  Note that in order for it to work, this
# module *must* have been imported (so that that below code has been run at least once).
# If the whole Pickling thing is a bit of a mystery, look it up in the Python docs - it's not as bad as it seems.

_lambdaName = (lambda: None).__name__ # static for identifying lambda instances

################
def _PickleMethod(methodInstance):
    """
    Workaround to allow Pickling of class variables that point to bound methods. 
    
    This code replaces the default Pickle algorithm for pickling methods.  It is a workaround for one of Pickle's 
    shortcomings - the fact that, out of the box, Pickle is not able to handle the serialisation of object instance attributes
    which point to bound methods.
    
    Note that lambdas still *cannot* be Pickled, there is no way around this.
    
    :param methodInstance: Class variable pointing to a bound method.
    """
    functionName = methodInstance.im_func.__name__
        
    obj = methodInstance.im_self
    cls = methodInstance.im_class
    
    if(functionName == _lambdaName):
        raise ValueError("Found bound lambda method %s (object=%s, type=%s), which is not compatable with the save mechanism. "
                         "Recommended you remove & restore this in object's __getstate__ and __setstate__ methods" 
                         % (functionName, obj, cls))
        
    return (_UnpickleMethod, (functionName, obj, cls))

################
def _UnpickleMethod(functionName, obj, cls):
    """
    Counterpart to _PickleMethod above - part of workaround to allow Pickling of variables pointing to bound methods.
    
    :param functionName: Name of the method as a string.
    :param obj: Instance of the class being Pickled.
    :param cls: The class type.
    """
    for clsCandidate in cls.mro():
        try:
            function = clsCandidate.__dict__[functionName]
        except KeyError:
            pass
        else:
            break
    return function.__get__(obj, cls)

################
copy_reg.pickle(types.MethodType, _PickleMethod, _UnpickleMethod) # "swizzles" the Pickle methods to use the workarounds defined above.

