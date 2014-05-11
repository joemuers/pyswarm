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


from boidBaseObject import PyswarmObject

import math as mth
import random as rand

import vector2 as bv2


def IsVector2(otherVector):
    return type(otherVector) is bv2.Vector2

def IsVector3(otherVector):
    return type(otherVector) is Vector3


__MAGNITUDE_UNDEFINED__ = -1.0

class Vector3(PyswarmObject):
    """
    3D vector with various trig functions.  
    
    Most classes in this package now use vector3, not 2. Although
    Vector3 has been written to be more or less backwards compatable
    (i.e. can be used in place of a bv2 and will still behave correctly).
    As such, note that self.u is interchangeable with self.x, and self.v is interchangeable
    with self.z.
    
    Note also that currently all angles are in degrees, not radians.
    """
    
    def __init__(self, x=0, y=0, z=0):
        """
        Note that you can either: 
        - pass in a vector object as an argument to create a (deep) copy
        - pass in numerical values for each axis
        - pass nothing for default values (0,0,0).
        """
        if(IsVector3(x)):
            self._x = x.x
            self._y = x.y
            self._z = x.z
        elif(IsVector2(x)):
            self._x = x.x
            self._y = 0
            self._z = x.z
        else:
            self._x = float(x)
            self._y = float(y)
            self._z = float(z)
   
        self._magnitude = __MAGNITUDE_UNDEFINED__
        self._magnitudeSquared = __MAGNITUDE_UNDEFINED__
        self._2dMagnitude = __MAGNITUDE_UNDEFINED__
        self._2dMagnitudeSquared = __MAGNITUDE_UNDEFINED__
        
    

####################### 
    def __str__(self):
        return "<x=%.4f, y=%.4f, z=%.4f>" % (self.x, self.y, self.z)

#####################    
    def _getMetaStr(self):
        magStr = ("%.4f" % self._magnitude) if(self._magnitude != __MAGNITUDE_UNDEFINED__) else "notCalc\'d"
        magSqStr = ("%.4f" % self._magnitudeSquared) if(self._magnitudeSquared != __MAGNITUDE_UNDEFINED__) else "notCalc\'d"
        twoDMagStr = ("%.4f" % self._2dMagnitude) if(self._2dMagnitude != __MAGNITUDE_UNDEFINED__) else "notCalc\'d"
        twoDMagSqStr = ("%.4f" % self._2dMagnitudeSquared) if(self._2dMagnitudeSquared != __MAGNITUDE_UNDEFINED__) else "notCalc\'d"
        
        return ("<mag=%s, magSqu=%s, 2dMag=%s, 2dMagSqu=%s>" % (magStr, magSqStr, twoDMagStr, twoDMagSqStr))
    
##################### 
    def __add__(self, other):
        if(IsVector2(other)):
            return Vector3(self.x + other.u, self.y, self.z + other.v)
        else:
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if(IsVector2(other)):
            return Vector3(self.x - other.u, self.y, self.z - other.v)
        else:
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, value):
        multipliedVector = Vector3(self.x * value, self.y * value, self.z * value)
        
        if(self._magnitude != __MAGNITUDE_UNDEFINED__):
            multipliedVector._magnitude = self._magnitude * value
            multipliedVector._magnitudeSquared = self._magnitude **2
        if(self._2dMagnitude != __MAGNITUDE_UNDEFINED__):
            multipliedVector._2dMagnitude = self._2dMagnitude * value
            multipliedVector._2dMagnitudeSquared = self._2dMagnitude **2

        return multipliedVector
    
    def __rmul__(self, value):
        return self.__mul__(value)
    
    def __div__(self, value):
        dividedVector = Vector3(self.x / value, self.y / value, self.z / value)
        
        if(self._magnitude != __MAGNITUDE_UNDEFINED__):
            dividedVector._magnitude = self._magnitude / value
            dividedVector._magnitudeSquared = self._magnitude **2
        if(self._2dMagnitude != __MAGNITUDE_UNDEFINED__):
            dividedVector._2dMagnitude = self._2dMagnitude / value
            dividedVector._2dMagnitudeSquared = self._2dMagnitude **2
            
        return dividedVector
    
    def __rdiv__(self, value):
        return self.__div__(1/value)

    def __imul__(self, value):        
        self._x *= value
        self._y *= value
        self._z *= value
        if(self._magnitudeSquared != __MAGNITUDE_UNDEFINED__):
            self._magnitudeSquared *= value
            if(self._magnitude != __MAGNITUDE_UNDEFINED__):
                self._magnitude *= value
        if(self._2dMagnitudeSquared != __MAGNITUDE_UNDEFINED__):
            self._2dMagnitudeSquared *= __MAGNITUDE_UNDEFINED__
            if(self._2dMagnitude != __MAGNITUDE_UNDEFINED__):
                self._magnitude *= value
            
        return self
    
    def __idiv__(self, value):
        self.divide(value)
        return self

    def __eq__(self, other):
        return IsVector3(other) and self.x == other.x and self.y == other.y and self.z == other.z
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __lt__(self, other):
        return IsVector3(other) and self.magnitudeSquared() < other.magnitudeSquared()
    
    def __gt__(self, other):
        return not IsVector3(other) or self.magnitudeSquared() > other.magnitudeSquared()
    
    def __nonzero__(self):
        return not self.isNull()

####################### 
    def _get_x(self):
        return self._x
    def _set_x(self, value):
        if(value != self._x):
            self._magnitudeSquared = __MAGNITUDE_UNDEFINED__
            self._2dMagnitudeSquared = __MAGNITUDE_UNDEFINED__
            self._x = value
    x = property(_get_x, _set_x)
    u = property(_get_x, _set_x) # for compatibility with Vector2
    
    def _get_y(self):
        return self._y
    def _set_y(self, value):
        if(value != self._y):
            self._magnitudeSquared = __MAGNITUDE_UNDEFINED__
            self._y = value
    y = property(_get_y, _set_y)
    
    def _get_z(self):
        return self._z
    def _set_z(self, value):
        if(value != self._z):
            self._magnitudeSquared = __MAGNITUDE_UNDEFINED__
            self._2dMagnitudeSquared = __MAGNITUDE_UNDEFINED__
            self._z = value
    z = property(_get_z, _set_z)
    v = property(_get_z, _set_z) # for compatibility with Vector2

#######################
    def _getValueAsTuple(self):
        return (self.x, self.y, self.z)
    def _setValueAsTuple(self, value):
        self.x = value[0]
        self.y = value[1]
        self.z = value[2]
    valueAsTuple = property(_getValueAsTuple, _setValueAsTuple)

#######################    
    def setValueFromString(self, valueString):
        """
        Mainly for compatability with attribute types.
        
        :param valueString: example string: <x=1.0,y=2.5,z=5.0>
        """
        tokens = valueString.strip(" <>").split(', ')
        
        self.x = float(tokens[0].lstrip('x='))
        self.y = float(tokens[1].lstrip('y='))
        self.z = float(tokens[2].lstrip('z='))
        
#######################     
    def isNull(self, ignoreVertical=False):
        """
        Returns True if x, y and z are all == zero, False otherwise.
        """
        return (self.x == 0 and self.z == 0 and (ignoreVertical or self.y == 0))
    
#######################
    def add(self, otherVector, ignoreVertical=False):
        """
        Adds self to another vector.
        :param otherVector: Vector2 or Vector3.
        :param ignoreVertical: ignores y if True.
        """
        
        self.x += otherVector.u
        self.z += otherVector.v
        if(not ignoreVertical): # and not IsVector2(otherVector):
            self.y += otherVector.y

#######################
    def subtract(self, otherVector, ignoreVertical=False):
        """
        Subtracts another vector from self.
        :param otherVector: Vector2 or Vector3.
        :param ignoreVertical: ignores y if True.
        """
        self.x -= otherVector.u
        self.z -= otherVector.v
        if(not ignoreVertical): # and not IsVector2(otherVector):
            self.y -= otherVector.y

#######################                 
    def divide(self, scalarVal, ignoreVertical=False):
        """
        Divides self by a scalar amount.
        :param scalarVal: float, scalar amount to divide by.
        :param ignoreVertical: ignores y if True.
        """
        scalarMult = 1.0 / scalarVal
        
        self._x *= scalarMult
        self._z *= scalarMult
        if(not ignoreVertical or self._y == 0): 
            self._y *= scalarMult
            if(self._magnitudeSquared != __MAGNITUDE_UNDEFINED__):
                self._magnitudeSquared *= scalarMult
                if(self._magnitude != __MAGNITUDE_UNDEFINED__):
                    self._magnitude *= scalarMult
        else:
            self._magnitudeSquared = __MAGNITUDE_UNDEFINED__
        
        if(self._2dMagnitudeSquared != __MAGNITUDE_UNDEFINED__):
            self._2dMagnitudeSquared *= scalarMult
            if(self._2dMagnitude != __MAGNITUDE_UNDEFINED__):
                self._2dMagnitude *= scalarMult

#######################
    def horizontalVector(self):
        """
        Returns Vector2 equivalent of self.
        """
        return bv2.Vector2(self.x, self.z)
    
#######################
    def degreeHeading(self):
        """
        Returns absolute, horizontal, degree heading of the vector (where <x=0,z=1> is 0 degrees).
        Ignores vertical component.
        """
        return self.horizontalVector().degreeHeading()

#######################
    def degreeHeadingVertical(self):
        """
        Returns "vertical" heading in degrees, where:
            - +90 = vertical up
            - -90 = vertical down
            -   0 = horizontal.
        """
        horizontalMag = self.horizontalVector().magnitude()
        
        if(horizontalMag > 0):
            return mth.degrees(mth.atan(self.y / horizontalMag))
        elif(self.y == 0):
            return 0
        else:
            return 90 if self.y > 0 else -90

#######################         
    def reset(self, x=0, y=0, z=0):
        """
        Resets x, y, z to given values.
        
        :param x: float, x val.
        :param y: float, y val.
        :param z: float, z val.
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

####################### 
    def resetToVector(self, otherVector, ignoreVertical=False):
        """
        Resets self to other vector's values, including magnitude if calculated.
        
        :param otherVector: Vector2 or Vector3.
        :param ignoreVertical: ignores y if True.
        """
        self._x = otherVector.u
        self._z = otherVector.v
        if(not ignoreVertical):
            if(IsVector2(otherVector)):
                self.y = 0
                self._2dMagnitude = otherVector._magnitude
                self._2dMagnitudeSquared = otherVector._magnitudeSquared
            else:
                self._y = otherVector.y
                self._magnitude = otherVector._magnitude
                self._magnitudeSquared = otherVector._magnitudeSquared
                self._2dMagnitude = otherVector._2dMagnitude
                self._2dMagnitudeSquared = otherVector._2dMagnitudeSquared
        else:
            self.y = 0

####################### 
    def invert(self):
        """
        Inverts self, magnitude remains unchanged.
        """
        self._x = -(self._x) # magnitude won't change, so don't use the property setter
        self._y = -(self._y) #
        self._z = -(self._z) #
        
##################### 
    def inverseVector(self):
        """
        Returns copy of self with inverted values. 
        """
        invertedVector = Vector3(-(self.x), -(self.y), -(self.z))
        invertedVector._magnitude = self._magnitude
        invertedVector._magnitudeSquared = self._magnitudeSquared
        invertedVector._2dMagnitude = self._2dMagnitude
        invertedVector._2dMagnitudeSquared = self._2dMagnitudeSquared
        
        return invertedVector

####################### 
    def magnitude(self, ignoreVertical=False):
        """
        Returns scalar magnitude of self, recalculating if necessary.
        Prefer magnitudeSquared where possible for performance reasons. 
        
        :param ignoreVertical: ignores y if True.
        """
        if(not ignoreVertical):
            if(self._magnitude == __MAGNITUDE_UNDEFINED__ or self._magnitudeSquared == __MAGNITUDE_UNDEFINED__):
                self._magnitude = mth.sqrt(self.magnitudeSquared(ignoreVertical))
            return self._magnitude
        else:
            if(self._2dMagnitude == __MAGNITUDE_UNDEFINED__ or self._2dMagnitudeSquared == __MAGNITUDE_UNDEFINED__):
                self._2dMagnitude = mth.sqrt(self.magnitudeSquared(ignoreVertical))
            return self._2dMagnitude  
        
#######################   
    def magnitudeSquared(self, ignoreVertical=False):
        """
        Returns square of scalar magnitude of self, recalculating if necessary.
        Prefer to magnitude if possible, for performance reasons.
        
        :param ignoreVertical: ignores y if True.
        """
        if(not ignoreVertical):
            if(self._magnitudeSquared == __MAGNITUDE_UNDEFINED__):
                self._magnitudeSquared = (self.x **2) + (self.y **2) + (self.z **2)
            return self._magnitudeSquared
        else:
            if(self._2dMagnitudeSquared == __MAGNITUDE_UNDEFINED__):
                self._2dMagnitudeSquared = (self.x **2) + (self.z **2)
            return self._2dMagnitudeSquared

####################### 
    def dot(self, otherVector, ignoreVertical=False):
        """
        Returns dot product of self with other vector.
        :param otherVector: Vector2 or Vector3.
        :param ignoreVertical: ignores y if True.
        """
        if(ignoreVertical or IsVector2(otherVector)):
            return (self.x * otherVector.u) + (self.z * otherVector.v)
        else:
            return (self.x * otherVector.x) + (self.y * otherVector.y) + (self.z * otherVector.z)

#######################        
    def cross(self, otherVector, ignoreVertical=False):
        """
        Returns cross product of self with other vector. 
        :param otherVector: Vector2 or Vector3.
        :param ignoreVertical: ignores y if True.
        """
        if(ignoreVertical or IsVector2(otherVector)):
            return (self.u * otherVector.v) - (self.v * otherVector.u)
        else:
            return (((self.y * otherVector.z) - (otherVector.y * self.z)) - 
                    ((self.x * otherVector.z) - (otherVector.x * self.z)) -
                    ((self.x * otherVector.y) - (otherVector.x * self.y)))

#######################
    def normalise(self, scaleFactor=1.0):
        """
        Normalises self into a unit vector equal in magnitude to given scale factor.
        
        :param scaleFactor:   float, will be the magnitude of the normalised vector.
        """
        if(self._magnitude != scaleFactor and not self.isNull()):
            multiple = scaleFactor / self.magnitude()
            self.x *= multiple
            self.y *= multiple
            self.z *= multiple
            
            self._magnitude = scaleFactor
            self._magnitudeSquared = scaleFactor **2
 
#######################            
    def normalisedVector(self, scaleFactor=1.0):
        """
        Returns a normalised copy of self, equal in magnitude to given scale factor.
        
        :param scaleFactor:  float, will be the magnitude of the normalised vector.
        """
        normalisedVector = Vector3(self.x, self.y, self.z)
        normalisedVector._magnitude = self._magnitude
        normalisedVector._magnitudeSquared = self._magnitudeSquared
        normalisedVector.normalise(scaleFactor)
        
        return normalisedVector

####################### 
    def angleTo(self, otherVector, ignoreVertical=True):
        """
        Returns angle TO other vector FROM this vector in DEGREES (negative for anti-clockwise).
        
        :param otherVector: Vector2 or Vector3.
        :param ignoreVertical:  ignores y if True.
        """
        if(self.isNull(ignoreVertical) or otherVector.isNull(ignoreVertical)):
            return 0
        elif(ignoreVertical or IsVector2(otherVector)):
            temp = self.dot(otherVector, True) / (self.magnitude(True) * otherVector.magnitude(True))
            if(temp < -1): #this shouldn't be happening, but it does (rounding errors??) so...
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
        else:
            return self.angleFrom3DVector(otherVector)
    
########
    def angleFrom(self, otherVector, ignoreVertical=True):
        """
        Returns angle FROM other vector TO this vector in DEGREES (negative for anti-clockwise).
                
        :param otherVector: Vector2 or Vector3.
        """
        angleTo = self.angleTo(otherVector, ignoreVertical)
        return -angleTo

####################### 
    def angleFrom3DVector(self, otherVector):
        """
        Returns angle, in degrees, between the two vectors in 3D space.
        
        :param otherVector: Vector3 instance.
        """
        vector1 = self.normalisedVector()
        vector2 = otherVector.normalisedVector()
        
        if(vector1 == vector2): # This whole bit could definitely be optimised if necessary
            return 0
        elif(vector1 == vector2.inverseVector()):
            return 180
        else:
            return mth.degrees(mth.acos(vector1.dot(vector2)))

#######################     
    def distanceFrom(self, otherVector, ignoreVertical=True): 
        """
        Returns scalar magnitude of distance to other vector.
        Prefer distanceSquaredFrom where possible for performance reasons.
        
        :param otherVector:  Vector2 or Vector3.
        :param ignoreVertical: ignores y if True.
        """
        return mth.sqrt(self.distanceSquaredFrom(otherVector, ignoreVertical))
        
########
    def distanceSquaredFrom(self, otherVector, ignoreVertical=True):
        """
        Returns distance magnitude squared to other vector.
        Prefer to distanceFrom where possible for performance reasons.
        
        :param otherVector: Vector2 or Vector3.
        :param ignoreVertical: ignores y if True.
        """
        if(ignoreVertical or IsVector2(otherVector)):
            tempU = (self.x - otherVector.u) ** 2
            tempV = (self.z - otherVector.v) ** 2
            
            return (tempU + tempV)
        else:
            tempX = (self.x - otherVector.x) ** 2
            tempY = (self.y - otherVector.y) ** 2
            tempZ = (self.z - otherVector.z) ** 2

            return(tempX + tempY + tempZ)
 
#######################       
    def isAbove(self, otherVector):
        """
        Returns True if above (y dimension) other vector, false otherwise.
        
        :param otherVector: Vector2 or Vector3.
        """
        if(IsVector2(otherVector)):
            return self.y > 0
        else:
            return self.y > otherVector.y

#######################  
    def rotateInHorizontal(self, angle):
        """
        Rotates vector in horizontal plane ONLY, by given angle.
        
        :param angle:  float, angle to rotate in DEGREES.  Negative values for anti-clockwise.
        """
        theta = mth.radians(-angle) #formula I'm using gives an inverted angle for some reason...??
        cosTheta = mth.cos(theta)
        sinTheta = mth.sin(theta)
        xTemp = self.x
        
        # magnitude should be unaffected => don't set values with property accessors
        self._x = (self.x * cosTheta) - (self.z * sinTheta)
        self._z = (xTemp * sinTheta) + (self.z * cosTheta)

####################### 
    def moveTowards(self, toVector, byAmount, ignoreVertical=True):
        """
        Moves towards a given position by given scalar amount.
        
        :param toVector: Vector2 or Vector3. Treated as a coordinate, not a vector.
        :param byAmount: float, distance to move.
        :param ignoreVertical: ignores y if True.
        """
        diffVec = toVector - self
        diffMagSquared = diffVec.magnitudeSquared(ignoreVertical)
        
        if(diffMagSquared < (byAmount ** 2)):
            self.resetToVector(toVector, ignoreVertical)
        else:
            diffVec.normalise(byAmount)
            self.x += diffVec.u
            if(not ignoreVertical):
                self.y += diffVec.y
            self.z += diffVec.v

#######################                 
    def jitter(self, maxAmount, ignoreVertical=True):
        """
        Makes a random change to both U and V by given amount.
        
        :param maxAmount: float, +/- (i.e. absolute) maximum value of change.
        :param ignoreVertical: ignores y if True.
        """
        self.x += rand.uniform(-maxAmount, maxAmount)
        if(not ignoreVertical):
            self.y += rand.uniform(-maxAmount, maxAmount)
        self.z += rand.uniform(-maxAmount, maxAmount)

################################################################################
    