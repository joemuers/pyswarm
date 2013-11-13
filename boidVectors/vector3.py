from boidBaseObject import BoidBaseObject

import math as mth
import random as rand

import vector2 as bv2


def IsVector2(otherVector):
    return type(otherVector) is bv2.Vector2


class Vector3(BoidBaseObject):
    """3D vector with various trig functions.  
    Most classes in this package now use vector3, not 2. Although
    Vector3 has been written to be more or less backwards compatable
    (i.e. can be used in place of a bv2 and will still behave correctly).
    As such, note that self.u is interchangeable with self.x, and self.v is interchangeable
    with self.z.
    
    Note also that currently all angles are in degrees, not radians.
    """
    
    def __init__(self, x=0, y=0, z=0):
        """Note that you can either: 
        - pass in a vector object as an argument to create a (deep) copy
        - pass in numerical values for each axis
        - pass nothing for default values (0,0,0).
        """
        if(type(x) is Vector3):
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
   
        self._needsMagCalc = True
        self._magnitude = -1.0
        self._needs2dMagCalc = True
        self._2dMagnitude = -1.0
        
    

####################### 
    def __str__(self):
        return "<x=%.4f, y=%.4f, z=%.4f>" % (self.x, self.y, self.z)

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

    def __imul__(self, value):
        magToo = not self._needsMagCalc
        
        self.x *= value
        self.y *= value
        self.z *= value
        if(magToo):
            self._magnitude *= value
            self._needsMagCalc = False
            
        return self
    
    def __idiv__(self, value):
        self.divide(value)
        return self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

####################### 
    def _get_x(self):
        return self._x
    def _set_x(self, value):
        if(value != self._x):
            self._needsMagCalc = True
            self._needs2dMagCalc = True
            self._x = value
    x = property(_get_x, _set_x)
    u = property(_get_x, _set_x) # for compatability with Vector2
    
    def _get_y(self):
        return self._y
    def _set_y(self, value):
        if(value != self._y):
            self._needsMagCalc = True
            self._y = value
    y = property(_get_y, _set_y)
    
    def _get_z(self):
        return self._z
    def _set_z(self, value):
        if(value != self._z):
            self._needsMagCalc = True
            self._needs2dMagCalc = True
            self._z = value
    z = property(_get_z, _set_z)
    v = property(_get_z, _set_z) # for compatability with Vector2
    
#######################
    def add(self, otherVector, ignoreVertical=False):
        self.x += otherVector.u
        self.z += otherVector.v
        if(not ignoreVertical): # and not IsVector2(otherVector):
            self.y += otherVector.y

#######################
    def subtract(self, otherVector, ignoreVertical=False):
        self.x -= otherVector.u
        self.z -= otherVector.v
        if(not ignoreVertical): # and not IsVector2(otherVector):
            self.y -= otherVector.y

#######################                 
    def divide(self, scalarVal, ignoreVertical=False):
        magToo = not ignoreVertical and not self._needsMagCalc
        scalarMult = 1.0 / scalarVal
        
        self.u *= scalarMult
        if(not ignoreVertical): # and not IsVector2(otherVector):
            self.y *= scalarMult
        self.v *= scalarMult
        if(magToo):
            self._magnitude *= scalarMult 
            self._needsMagCalc = False

#######################
    def horizontalVector(self):
        return bv2.Vector2(self.x, self.z)
    
#######################
    def degreeHeadingHorizontal(self):
        return self.horizontalVector().degreeHeading()

#######################
    def degreeHeadingVertical(self):
        horizontalMag = self.horizontalVector().magnitude()
        
        if(horizontalMag > 0):
            return mth.degrees(mth.atan(self.y / horizontalMag))
        elif(self.y == 0):
            return 0
        else:
            return 90 if self.y > 0 else -90

#######################     
    def isNull(self, ignoreVertical=False):
        return (self.x == 0 and self.z == 0 and (ignoreVertical or self.y == 0))

#######################         
    def reset(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

####################### 
    def resetVec(self, otherVector, ignoreVertical=False):
        self.x = otherVector.u
        if(not ignoreVertical):
            self.y = 0 if IsVector2(otherVector) else otherVector.y
        self.z = otherVector.v
        
        if(not ignoreVertical and not otherVector._needsMagCalc):
            self._magnitude = otherVector._magnitude
            self._needsMagCalc = False
        elif(ignoreVertical and not otherVector._needs2dMagCalc):
            self._2dMagnitude = otherVector._2dMagnitude
            self._needs2dMagCalc = False

####################### 
    def invert(self):
        self._x = -(self._x) # magnitude won't change, so don't use the property setter
        self._y = -(self._y) #
        self._z = -(self._z) #
        
##################### 
    def inverseVector(self):
        ret = Vector3(-(self.x), -(self.y), -(self.z))
        if(not self._needsMagCalc):
            ret._magnitude = self._magnitude
            ret._needsMagCalc = False
        return ret

####################### 
    def magnitude(self, ignoreVertical=False):
        if(not ignoreVertical):
            if(self._needsMagCalc):
                self._magnitude = mth.sqrt((self.x **2) + (self.y **2) + (self.z ** 2))
                self._needsMagCalc = False
            return self._magnitude
        else:
            if(self._needs2dMagCalc):
                self._2dMagnitude = mth.sqrt((self.x **2) + (self.z **2))
                self._needs2dMagCalc = False
            return self._2dMagnitude  

####################### 
    def dot(self, otherVector, ignoreVertical = False):
        if(ignoreVertical or IsVector2(otherVector)):
            return (self.x * otherVector.u) + (self.z * otherVector.v)
        else:
            return (self.x * otherVector.x) + (self.y * otherVector.y) + (self.z * otherVector.z)

#######################
    def normalise(self, scaleFactor=1.0):
        if(not self.isNull()):
            multiple = scaleFactor / self.magnitude()
            self.x *= multiple
            self.y *= multiple
            self.z *= multiple
            
            self._magnitude = scaleFactor
            self._needsMagCalc = False
 
#######################            
    def normalisedVector(self, scaleFactor=1.0):
        retVal = Vector3(self.x, self.y, self.z)
        if(not self._needsMagCalc):
            retVal._magnitude = self._magnitude
            retVal._needsMagCalc = False
        else:
            retVal.normalise(scaleFactor)
        return retVal

####################### 
    def angleFrom(self, otherVector, ignoreVertical=True):
        """angle between direction vectors in DEGREES (negative for anti-clockwise)."""
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

####################### 
    def angleFrom3DVector(self, otherVector):
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
        if(ignoreVertical or IsVector2(otherVector)):
            tempU = (self.x - otherVector.u) ** 2
            tempV = (self.z - otherVector.v) ** 2
            return mth.sqrt(tempU + tempV)
        else:
            tempX = (self.x - otherVector.x) ** 2
            tempY = (self.y - otherVector.y) ** 2
            tempZ = (self.z - otherVector.z) ** 2
            return mth.sqrt(tempX + tempY + tempZ)
 
#######################       
    def isAbove(self, otherVector):
        if(IsVector2(otherVector)):
            return self._y > 0
        else:
            return self._y > otherVector.y

#######################  
    def rotateInHorizontal(self, angle):
        """Rotates vector in horizontal plane ONLY"""
        theta = mth.radians(-angle) #formula I'm using gives an inverted angle for some reason...??
        cosTheta = mth.cos(theta)
        sinTheta = mth.sin(theta)
        xTemp = self.x
        
        self.x = (self.x * cosTheta) - (self.z * sinTheta)
        self.z = (xTemp * sinTheta) + (self.z * cosTheta)

####################### 
    def moveTowards(self, toVector, byAmount, ignoreVertical=True):
        diffVec = toVector - self
        if(ignoreVertical):
            diffVec = diffVec.horizontalVector()
        diffMag = diffVec.magnitude()
        
        if(diffMag < byAmount):
            self.resetVec(toVector, ignoreVertical)
        else:
            diffVec.normalise()
            diffVec *= byAmount
            self.x += diffVec.u
            if(not ignoreVertical):
                self.y += diffVec.y
            self.z += diffVec.v

#######################                 
    def jitter(self, maxAmount, ignoreVertical=True):
        self.x += rand.uniform(-maxAmount, maxAmount)
        if(not ignoreVertical):
            self.y += rand.uniform(-maxAmount, maxAmount)
        self.z += rand.uniform(-maxAmount, maxAmount)

################################################################################
    