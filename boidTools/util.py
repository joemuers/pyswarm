import boidVectors.vector3 as bv3

import pymel.core as pm
import pymel.core.nodetypes as pmn  # Eclipse doesn't like pm.nodetypes for some reason...
import logging



def PackageName():
    return "JMSwarm"

######################################
__utilLogger__ = logging.getLogger(PackageName())

def LogDebug(message, prefix=None):
    __utilLogger__.debug("%s %s" % (prefix, message) if(prefix is not None) else message)
    
def LogInfo(message, prefix=None):
    __utilLogger__.info("%s %s" % (prefix, message) if(prefix is not None) else message)
    
def LogWarning(message, prefix=None):
    __utilLogger__.warning("%s %s" % (prefix, message) if(prefix is not None) else message)
    
def LogError(message, prefix=None):
    __utilLogger__.error("%s %s" % (prefix, message) if(prefix is not None) else message)
    

######################################
def PymelObjectFromObjectName(objectName):
    return pm.PyNode(objectName)

######################################
def BoidVector3FromPymelLocator(locator):
    if(isinstance(locator, pmn.Locator)):
        coOrdsString = locator.getPosition()
        coOrds = coOrdsString.split()
        return bv3.Vector3(float(coOrds[0]), float(coOrds[1]), float(coOrds[2]))     
    else:
        return None
    
def BoidVectorOrderedPairFromPymelLocators(locatorA, locatorB):
    lowerBoundsVector = BoidVector3FromPymelLocator(locatorA)
    upperBoundsVector = BoidVector3FromPymelLocator(locatorB)
    
    if(lowerBoundsVector.x > upperBoundsVector.x):
        lowerBoundsVector.x, upperBoundsVector.x = upperBoundsVector.x, lowerBoundsVector.x
    if(lowerBoundsVector.y > upperBoundsVector.y):
        lowerBoundsVector.y, upperBoundsVector.y = upperBoundsVector.y, lowerBoundsVector.y
    if(lowerBoundsVector.z > upperBoundsVector.z):
        lowerBoundsVector.z, upperBoundsVector.z = upperBoundsVector.z, lowerBoundsVector.z
    
    return (lowerBoundsVector, upperBoundsVector)

######################################    
def PymelPointFromBoidVector3(boidVectors):
    return pm.datatypes.Point(boidVectors.x, boidVectors.y, boidVectors.z)

def BoidVector3FromPymelPoint(point):
    return bv3.Vector3(point.x, point.y, point.z)

######################################
def BoidVector3FromPymelVector(pymelVector):
    return bv3.Vector3(pymelVector.x, pymelVector.y, pymelVector.z)

def PymelVectorFromBoidVector3(boidVectors):
    return pm.datatypes.Vector(boidVectors.x, boidVectors.y, boidVectors.z)

######################################
def ParticleIdsListForParticleShape(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='particleId', a=True)

######################################
def ParticlePositionsListForParticleShape(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='worldPosition', a=True)

def GetSingleParticlePosition(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='worldPosition', id=particleId)

def SetParticlePosition(particleShapeName, particleId, position):
    """In general - DO NOT USE!!"""
    pm.particle(particleShapeName, e=True, at='velocity', id=particleId, vv=(position.x, position.y, position.z))    
    
######################################
def ParticleVelocitiesListForParticleShape(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='velocity', a=True)

def GetSingleParticleVelocity(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='velocity', id=particleId)

def SetSingleParticleVelocity(particleShapeName, particleId, velocityVector):
    """@param particleShapeName: particleShapeNode name.
    @param particleId: (self explanatory)
    @param velocityVector: boidVector.Vector3 instance.
    """
    #print("pid=%d, vel=%s" % (particleId, velocityVector))
    
    pm.particle(particleShapeName, e=True, at='velocity', id=particleId, 
                vv=(velocityVector.x, velocityVector.y, velocityVector.z))
    
######################################
def StickinessScalesListForParticleShape(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='stickinessScalePP', a=True)

def GetSingleParticleStickinessScale(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='stickinessScalePP', id=particleId)

def SetSingleParticleStickinessScale(particleShapeName, particleId, value):
    """1 == particleID, 2 = float value"""
    pm.particle(particleShapeName, e=True, at='stickinessScalePP', id=particleId, fv=value)
    
######################################
def KillParticle(particleShapeName, particleId):
    """IMPORTANT - WILL NOT TAKE EFEECT UNTIL AFTER NEXT FRAME UPDATE"""
    pm.particle(particleShapeName, e=True, at='lifespanPP', id=particleId, fv=0.0)
    
######################################
def SetParticleColour(particleShapeName, particleId, colour):
    if(type(colour) == tuple):
        pm.particle(particleShapeName, e=True, at="rgbPP", id=particleId, vv=(colour[0], colour[1], colour[2]))
    else: # assuming colour is a float => greyscalse colour
        pm.particle(particleShapeName, e=True, at="rgbPP", id=particleId, vv=(colour, colour, colour))
    
