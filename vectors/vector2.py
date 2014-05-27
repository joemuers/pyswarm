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


import random as rand
import math as mth

from pyswarm.pyswarmObject import PyswarmObject



__MAGNITUDE_UNDEFINED__ = -1.0



#####
def IsVector2(otherVector):
    return type(otherVector) == Vector2



#####
class Vector2(PyswarmObject):
    """
    2D vector with various trig functions.
    
    Initial implementation of PySwarm system used surface UV coordinates rather than 3D position, hence 
    this class.  However still comes in handy...
    
    Note that angle inputs/outputs, currently, are in degrees, NOT radians.
    """
    
    def __init__(self, u=0, v=0):
        """
        Note that you can either: 
        - pass in a vector object as an argument to create a (deep) copy
        - pass in numerical values for each axis
        - pass nothing for default values (0,0).
        """
        if(hasattr(u, "u")): # check if first argument is a Vector2/3 instance or not
            self._u = u.u
            self._v = u.v
        else:
            self._u = float(u)
            self._v = float(v)
        
        self._magnitude = __MAGNITUDE_UNDEFINED__
        self._magnitudeSquared = __MAGNITUDE_UNDEFINED__

####################### 
    def __str__(self):
        return "<u=%.4f, v=%.4f>" % (self.u, self.v)

#####################    
    def _getMetaStr(self):
        magStr = ("%.4f" % self._magnitude) if(self._magnitude != __MAGNITUDE_UNDEFINED__) else "notCalc\'d"
        magSqStr = ("%.4f" % self._magnitudeSquared) if(self._magnitudeSquared != __MAGNITUDE_UNDEFINED__) else "notCalc\'d"
        
        return ("<mag=%s, magSqu=%s>" % (magStr, magSqStr))

##################### 
    def __add__(self, other):
        return Vector2(self.u + other.u, self.v + other.v)

    def __sub__(self, other):
        return Vector2(self.u - other.u, self.v - other.v)
   
    def __imul__(self, value):
        self.u *= value
        self.v *= value
        return self

    def __idiv__(self, value):
        self.u /= value
        self.v /= value
        return self

    def __eq__(self, other):
        return IsVector2(other) and self.u == other.u and self.v == other.v
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return IsVector2(other) and self.magnitudeSquared() < other.magnitudeSquared()
    
    def __gt__(self, other):
        return not IsVector2(other) or self.magnitudeSquared() > other.magnitudeSquared()
    
    def __nonzero__(self):
        return not self.isNull()

####################### 
    def _get_u(self):
        return self._u
    def _set_u(self, value):
        if(value != self._u):
            self._magnitude = __MAGNITUDE_UNDEFINED__ 
            self._magnitudeSquared = __MAGNITUDE_UNDEFINED__
            self._u = value
    u = property(_get_u, _set_u)
    
    def _get_v(self):
        return self._v
    def _set_v(self, value):
        if(value != self._v):
            self._magnitude = __MAGNITUDE_UNDEFINED__ 
            self._magnitudeSquared = __MAGNITUDE_UNDEFINED__
            self._v = value
    v = property(_get_v, _set_v)
    
#######################
    def _getValueAsTuple(self):
        """
        Gets/sets value as tuple (u,v).
        """
        return (self.u, self.v)
    def _setValueAsTuple(self, value):
        self.u = value[0]
        self.v = value[1]
    valueAsTuple = property(_getValueAsTuple, _setValueAsTuple)
    
#######################
    def setValueFromString(self, valueString):
        """
        Mainly for compatability with attribute types.
        
        :param valueString: example string: <u=1.0,v=2.5>
        """
        tokens = valueString.strip(" <>").split(', ')
        
        self.u = float(tokens[0].lstrip('u='))
        self.v = float(tokens[1].lstrip('v='))
    
#######################     
    def isNull(self):
        """
        Returns True if u and v both == zero, False otherwise.
        """
        return (self._u == 0 and self._v == 0)

#######################         
    def reset(self, u = 0, v = 0):
        """
        Resets u and v to the given values.
        
        :param u: float, new U value.
        :param v: float, new V value.
        """
        self.u = float(u)
        self.v = float(v)

####################### 
    def resetToVector(self, otherVector):
        """
        Copies U, V and magnitude values from other vector.
        
        :param otherVector: can be Vector2, or Vector3 (magnitude ignored if so).
        """
        self.u = otherVector.u
        self.v = otherVector.v
        if(isinstance(otherVector, Vector2)):
            self._magnitudeSquared = otherVector._magnitudeSquared
            self._magnitude = otherVector._magnitude 

####################### 
    def invert(self):
        """
        Inverts U and V values, scalar magnitude is unchanged.
        """
        self._u = -(self._u) # magnitude won't change, so don't use accessor
        self._v = -(self._v) #
    
##################### 
    def inverseVector(self):
        """
        Returns copy of self with inverted U and V values.
        """
        return Vector2(-(self.u), -(self.v))

####################### 
    def magnitude(self, dummy=False): # dummy- so magnitude can be called interchangeably for Vector2/3. Very hacky, I know...
        """
        Returns scalar magnitude, recalculating if necessary.  
        Where possible, prefer magnitudeSquared for performance reasons. 
        
        :param dummy: not used, present for interchangeability with Vector3.
        """
        if(self._magnitude == __MAGNITUDE_UNDEFINED__):
            self._magnitude = mth.sqrt(self.magnitudeSquared())
        return self._magnitude
    
#######################
    def magnitudeSquared(self):
        """
        Returns square of the scalar magnitude, recalculating if necessary.
        If comparing distances, use mag squared as a more performant alternative to magnitude.
        """
        if(self._magnitudeSquared == __MAGNITUDE_UNDEFINED__):
            self._magnitudeSquared = (self._u **2) + (self._v **2)
        return self._magnitudeSquared

####################### 
    def dot(self, otherVector):
        """
        Returns the dot product with other vector.
        
        :param otherVector: Vector2 or Vector3.
        """
        return (self.u * otherVector.u) + (self.v * otherVector.v)

#######################    
    def cross(self, otherVector):
        """
        Returns cross product with other vector.
        
        :param otherVector: Vector2 or Vector3.
        """
        return (self.u * otherVector.v) - (self.v * otherVector.u)

#######################
    def normalise(self, scaleFactor=1.0):
        """
        Normalises self into a unit vector equal in magnitude to given scale factor.
        
        :param scaleFactor: float, will be the magnitude of the normalised vector.
        """
        if(self._magnitude != scaleFactor and not self.isNull()):
            multiple = scaleFactor / self.magnitude()
            self.u *= multiple
            self.v *= multiple
            self._magnitude = scaleFactor
            self._magnitudeSquared = scaleFactor **2

#######################
    def normalisedVector(self, scaleFactor=1.0):
        """
        Returns a normalised copy of self, equal in magnitude to given scale factor.
        
        :param scaleFactor:  float, will be the magnitude of the normalised vector.
        """
        normalisedVector = Vector2(self.u, self.v)
        normalisedVector.normalise(scaleFactor)
        return normalisedVector
    
#######################
    def degreeHeading(self):
        """
        Returns absolute degree heading of the vector, where (x=0,z=1) == 0 degrees.
        """
        zeroDegrees = Vector2(0, 1)
        heading = self.angleFrom(zeroDegrees)
        if(heading < 0):
            heading += 360
        return heading

####################### 
    def angleTo(self, otherVector):
        """
        Returns angle TO other vector FROM this vector in DEGREES (negative for anti-clockwise).
        
        :param otherVector: Vector2 or Vector3.
        """
        if(self.isNull() or otherVector.isNull()):
            return 0
        else:    
            temp = self.dot(otherVector) / (self.magnitude() * otherVector.magnitude())
            if(temp < -1): #this shouldn't be happening, but it does (rounding errors?) so...
                temp = -1
            elif(temp > 1):
                temp = 1
            
            angle = mth.degrees(mth.acos(temp))
            if(0 < angle and angle < 180):
                cross = (self.u * otherVector.v) - (self.v * otherVector.u)
                if(cross > 0):  # anti-clockwise
                    return -angle
                else: # clockwise
                    return angle
            else:
                return angle

########            
    def angleFrom(self, otherVector):
        """
        Returns angle FROM other vector TO this vector in DEGREES (negative for anti-clockwise).
                
        :param otherVector: Vector2 or Vector3.
        """
        angleTo = self.angleTo(otherVector)
        return -angleTo

#######################     
    def distanceFrom(self, otherVector):
        """
        Returns scalar magnitude of distance to other vector.
        Prefer distanceSquaredFrom where possible for performance reasons.
        
        :param otherVector:  Vector2 or Vector3.
        """
        return mth.sqrt(self.distanceSquaredFrom(otherVector))
    
########
    def distanceSquaredFrom(self, otherVector):
        """
        Returns distance magnitude squared to other vector.
        Prefer to distanceFrom where possible for performance reasons.
        
        :param otherVector:  Vector2 or Vector3.
        """
        tempU = (self.u - otherVector.u) ** 2
        tempV = (self.v - otherVector.v) ** 2
        return (tempU + tempV)

#######################
    def add(self, otherVector):
        """
        Adds other vector to self.
        
        :param otherVector:  Vector2 or Vector3.
        """
        self.u += otherVector.u
        self.v += otherVector.v

#######################                 
    def divide(self, scalarVal):
        """
        Divides self by the scalar values.
        
        :param scalarVal: float, scalar value.
        """
        self.u /= scalarVal
        self.v /= scalarVal

#######################  
    def rotate(self, angle):
        """
        Rotates self by given angle.
        
        :param angle: float, angle to rotate in DEGREES.  Negative values for anti-clockwise.
        """
        theta = mth.radians(-angle) #formula I'm using gives a reversed angle for some reason...??
        cosTheta = mth.cos(theta)
        sinTheta = mth.sin(theta)
        uTemp = self.u

        self.u = (self.u * cosTheta) - (self.v * sinTheta)
        self.v = (uTemp * sinTheta) + (self.v * cosTheta)

####################### 
    def moveTowards(self, toVector, byAmount):
        """
        Moves towards a given position by given scalar amount.
        
        :param toVector: Vector2 or Vector3 (will be treated as Vector2).  Treated as a coordinate, not a vector.
        :param byAmount: float, distance to move.
        """
        diffVec = toVector - self
        diffMag = diffVec.magnitude()

        if(diffMag.magnitudeSquared() < (byAmount **2)):
            self.resetToVector(toVector)
        else:
            diffVec.normalise(byAmount)
            self.u += diffVec.u
            self.v += diffVec.v

#######################                 
    def jitter(self, maxAmount):
        """
        Makes a random change to both U and V by given amount.
        
        :param maxAmount: float, +/- (i.e. absolute) maximum value of change.
        """
        self.u += rand.uniform(-maxAmount, maxAmount)
        self.v += rand.uniform(-maxAmount, maxAmount)

################################################################################
