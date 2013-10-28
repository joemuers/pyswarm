import pymel.core as pm
import pymel.core.nodetypes as pmn  # Eclipse doesn't like pm.nodetypes for some reason...
import boidVector3 as bv3


######################################
#def setParticleShapeName(particleShapeNode):
    #global particleShapeName
    #particleShapeName = particleShapeNode.name()

def boidVectorFromLocator(locator):
    if(type(locator) == pmn.Locator):
        coOrdsString = locator.getPosition()
        coOrds = coOrdsString.split()
        return bv3.BoidVector3(float(coOrds[0]), float(coOrds[1]), float(coOrds[2]))     
    else:
        return locator
    
def pymelPointFromBoidVector(boidVector):
    return pm.datatypes.Point(boidVector.x, boidVector.y, boidVector.z)

def boidVectorFromPymelPoint(point):
    return bv3.BoidVector3(point.x, point.y, point.z)

def boidVectorFromPymelVector(pymelVector):
    return bv3.BoidVector3(pymelVector.x, pymelVector.y, pymelVector.z)

def pymelVectorFromBoidVector(boidVector):
    return pm.datatypes.Vector(boidVector.x, boidVector.y, boidVector.z)

def getParticleIdsList(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='particleId', a=True)


######################################
def getParticlePositionsList(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='worldPosition', a=True)

def getSingleParticlePosition(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='worldPosition', id=particleId)


######################################
def getParticleVelocitiesList(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='velocity', a=True)

def getSingleParticleVelocity(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='velocity', id=particleId)

def setParticleVelocity(particleShapeName, particleId, velocityVector):
    """1 == particleID, 2 = boid3Vector"""
    
    #print("pid=%d, vel=%s" % (particleId, velocityVector))
    
    pm.particle(particleShapeName, e=True, at='velocity', id=particleId, 
                vv=(velocityVector.x, velocityVector.y, velocityVector.z))
    
######################################
def getStickinessScalesList(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='stickinessScalePP', a=True)

def getSingleParticleStickinessScale(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='stickinessScalePP', id=particleId)

def setStickinessScale(particleShapeName, particleId, value):
    """1 == particleID, 2 = float value"""
    pm.particle(particleShapeName, e=True, at='stickinessScalePP', id=particleId, fv=value)
    
def setPosition(particleShapeName, particleId, position):
    """In general - DO NOT USE!"""
    pm.particle(particleShapeName, e=True, at='velocity', id=particleId, vv=(position.x, position.y, position.z))    
    
######################################
def killParticle(particleShapeName, particleId):
    """IMPORTANT - WILL NOT TAKE EFEECT UNTIL AFTER NEXT FRAME UPDATE"""
    pm.particle(particleShapeName, e=True, at='lifespanPP', id=particleId, fv=0.0)
    
######################################
def setParticleColour(particleShapeName, particleId, red, green, blue):
    pm.particle(particleShapeName, e=True, at="rgbPP", id=particleId, vv=(red, green, blue))