
class BoidObject(object):
    """Base class for all the other boid classes in this package.  Treated as an abstract class, I
    suppose, although technically it isn't one.
    Raison d'etre just to kind of formalise the 'metaStr' implementation...
    
    Throughout the classes in this package, metaStr is kind of a complement to the usual
    __str__ method but giving info on the more 'meta' attributes.  Purely for logging/debugging.
    """
    
    def metaStr(self):
        return self.__str__()