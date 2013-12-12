
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
        return "(Meta string not implemented for this class)"
    metaStr = property(lambda obj:obj._getMetaStr())  # the lambda complication is necessary to make this property
    #                                                 # accessor work correctly with the inheritance heirarchy.