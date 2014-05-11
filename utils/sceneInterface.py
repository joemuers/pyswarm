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


import vectors.vector3 as v3
import utils.general as util

import pymel.core as pm
import pymel.core.nodetypes as pmn  # Eclipse doesn't like pm.nodetypes for some reason... 
import pymel.core.language as la    # (perhaps an issue with the Pymel predefinitions?)
import maya.cmds as cmds


######################################
def PymelObjectFromObjectName(objectName, bypassTransformNodes=True, pymelType=None):
    """Converts Maya object string to a Pymel object, if necessary.
    If the object is already a Pymel object, no action is taken.
    """
    if(isinstance(objectName, pm.PyNode)):
        result = _GetPymelObjectWithType(objectName, pymelType) if(bypassTransformNodes) else objectName 
    else:
        value = pm.PyNode(objectName)
        result = _GetPymelObjectWithType(value, pymelType) if(bypassTransformNodes) else value 
        
    if(pymelType is None or isinstance(result, pymelType)):
        return result
    else:
        raise TypeError("Cannot make Pymel object from %s - needed type %s, got %s" % 
                        (objectName, pymelType, type(objectName)))
    
######################################
def GetSelectedParticleShapeNodes(particleShapeName=None, suppressPymelBugWarning=False):
    selectionList = []
    try:
        selectionList = pm.ls(selection=True)
    except Exception:
        if(not suppressPymelBugWarning):
            util.LogWarning("There's a bug in earlier versions of Maya's PyMel - it can break if you have individual "
                            "particles selected (i.e. in component mode). Nothing I can do about that unfortunately. "
                            "You may want to try again *without* individual particles selected.")
        
    returnList = []
    for selectedObject in selectionList:
        result = _GetPymelObjectWithType(selectedObject, ParticlePymelType())
        if(result is not None and 
           (particleShapeName is None or result.name() == particleShapeName)):
            returnList.append(result)

    return returnList

######################################
def GetSelectedParticles(particleShapeName):
    if(GetSelectedParticleShapeNodes(particleShapeName, suppressPymelBugWarning=True)):
        return ParticleIdsListForParticleShape(particleShapeName)
    else:
        # using cmds instead of PyMel as a workaround here - there's a bug in earlier versions
        # of PyMel where the 'ls' command breaks if you have particle components selected (nice!)
        selectionList = cmds.ls(selection=True)
        returnList = []
        for selectedObject in selectionList:
            if(cmds.objectType(selectedObject, isType="nParticle")):
                particleComponentStrings = selectedObject.split(".pt[")
                candidateName = particleComponentStrings[0]
                if(candidateName == particleShapeName):
                    index = int( particleComponentStrings[1].strip(']') )
                    returnList.append(index)
                    
        return returnList
    
######################################
def SelectParticlesInList(particleIds, particleShapeName):
    def _addToSelection(rangeStart, rangeEnd, particleShapeName):
        indexSpecifier = (str(rangeStart) if(rangeStart == rangeEnd) else ("%d:%d" % (rangeStart, rangeEnd)))
        pm.select(("%s.pt[%s]" % (particleShapeName, indexSpecifier)), add=True)
    
    pm.select(clear=True)
    rangeStart = -1
    rangeEnd = -1
    for particleId in sorted(particleIds):
        if(rangeStart == -1):
            rangeStart = particleId
            rangeEnd = particleId
        elif(particleId == rangeEnd + 1):
            rangeEnd = particleId
        else:
            _addToSelection(rangeStart, rangeEnd, particleShapeName)
            rangeStart = particleId
            rangeEnd = particleId
    
    if(rangeStart != -1):
        _addToSelection(rangeStart, rangeEnd, particleShapeName)

######################################
def GetSelectedLocators():
    selectionList = []
    try:
        selectionList = pm.ls(selection=True)
    except Exception:
        util.LogWarning("There's a bug in earlier versions of Maya's PyMel - it can break if you have individual "
                        "particles selected (i.e. in component mode). Nothing I can do about that unfortunately. "
                        "You may want to try again *without* individual particles selected.")
    returnList = []
    for selectedObject in selectionList:
        result = _GetPymelObjectWithType(selectedObject, LocatorPymelType())
        if(result is not None):
            returnList.append(result)
    
    return returnList

######################################
def GetObjectsInSceneOfType(pymelType):
    return [pymelObject for pymelObject in pm.ls() if(isinstance(pymelObject, pymelType))]
    
######################################
def _GetPymelObjectWithType(pymelObject, pymelType):
    """Checks given object is of correct type.
    Will inspect the corresponding shape node if a transform node is given.
    """
    if(pymelType is not None and isinstance(pymelObject, pymelType)):
        return pymelObject
    elif(isinstance(pymelObject, pmn.Transform)):
        shapeNode = pymelObject.getShape()
        if((pymelType is None and isinstance(pymelObject, pm.PyNode)) or 
           isinstance(shapeNode, pymelType)):
            return shapeNode
    elif(pymelType is None and isinstance(pymelObject, pm.PyNode)):
        return pymelObject

    return None

######################################
def GetNucleusSpaceScale():
    nucleus = pm.ls(la.mel.getActiveNucleusNode(False, True))[0]
    return nucleus.attr('spaceScale').get()

######################################
def LocatorPymelType():
    return pmn.Locator

def ParticlePymelType():
    return pmn.NParticle

def CurvePymelType():
    return pmn.NurbsCurve

######################################



######################################
def Vector3FromLocator(locator):
    if(isinstance(locator, pmn.Locator)):
        coOrdsString = locator.getPosition()
        coOrds = coOrdsString.split()
        return v3.Vector3(float(coOrds[0]), float(coOrds[1]), float(coOrds[2]))     
    elif(isinstance(locator, basestring)):
        return Vector3FromLocator(PymelObjectFromObjectName(locator))
    else:
        return None

#####    
def Vector3OrderedPairFromLocators(locatorA, locatorB):
    lowerBoundsVector = Vector3FromLocator(locatorA)
    upperBoundsVector = Vector3FromLocator(locatorB)
    
    if(lowerBoundsVector.x > upperBoundsVector.x):
        lowerBoundsVector.x, upperBoundsVector.x = upperBoundsVector.x, lowerBoundsVector.x
    if(lowerBoundsVector.y > upperBoundsVector.y):
        lowerBoundsVector.y, upperBoundsVector.y = upperBoundsVector.y, lowerBoundsVector.y
    if(lowerBoundsVector.z > upperBoundsVector.z):
        lowerBoundsVector.z, upperBoundsVector.z = upperBoundsVector.z, lowerBoundsVector.z
    
    return (lowerBoundsVector, upperBoundsVector)

######################################    
def PymelPointFromVector3(vector3):
    return pm.datatypes.Point(vector3.x, vector3.y, vector3.z)

#####
def Vector3FromPymelPoint(point):
    return v3.Vector3(point.x, point.y, point.z)

######################################
def Vector3FromPymelVector(pymelVector):
    return v3.Vector3(pymelVector.x, pymelVector.y, pymelVector.z)

#####
def PymelVectorFromVector3(vector3):
    return pm.datatypes.Vector(vector3.x, vector3.y, vector3.z)

######################################



######################################
def ParticleIdsListForParticleShape(particleShapeName):
    return map(int, pm.getParticleAttr(particleShapeName + ".pt[:]", at='particleId', a=True))

######################################
def ParticlePositionsListForParticleShape(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='worldPosition', a=True)

#####
def GetSingleParticlePosition(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='worldPosition', id=particleId)

#####
def SetParticlePosition(particleShapeName, particleId, position):
    """In general - DO NOT USE!!"""
    pm.particle(particleShapeName, e=True, at='velocity', id=particleId, vv=(position.x, position.y, position.z))    
    
######################################
def ParticleVelocitiesListForParticleShape(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='velocity', a=True)

#####
def GetSingleParticleVelocity(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='velocity', id=particleId)

#####
def SetSingleParticleVelocity(particleShapeName, particleId, velocityVector):
    """@param particleShapeName: particleShapeNode name.
    @param particleId: (self explanatory)
    @param velocityVector: vectors.Vector3 instance.
    """
    #print("pid=%d, vel=%s" % (particleId, velocityVector))
    
    pm.particle(particleShapeName, e=True, at='velocity', id=particleId, 
                vv=(velocityVector.x, velocityVector.y, velocityVector.z))
    
######################################
def StickinessScalesListForParticleShape(particleShapeName):
    return pm.getParticleAttr(particleShapeName + ".pt[:]", at='stickinessScalePP', a=True)

#####
def GetSingleParticleStickinessScale(particleShapeName, particleId):
    return pm.particle(particleShapeName, q=True, at='stickinessScalePP', id=particleId)

#####
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

######################################        
def AddStickinessPerParticleAttributeIfNecessary(particleShapeName):
    if(not pm.attributeQuery('stickinessScalePP', node=particleShapeName, exists=True)):
        pm.addAttr(particleShapeName, longName='stickinessScalePP', dataType='doubleArray')
        util.LogDebug("Added PP attribute stickinessScalePP to %s" % particleShapeName)
    if(not pm.attributeQuery('stickinessScalePP0', node=particleShapeName, exists=True)):
        pm.addAttr(particleShapeName, longName='stickinessScalePP0', dataType='doubleArray')
        util.LogDebug("Added PP attribute stickinessScalePP0 to %s" % particleShapeName)
        
#######################################



#######################################
def QuickSceneSetup(particleShapeName, 
                    enableSelfCollide=True, disableFriction=True, disableIgnoreGravity=True,
                    changeRenderType=True, enableGroundPlane=True, changeSpaceScale=True,
                    translateAbovePlane=True):
    
    util.LogInfo("Performing quick scene setup...")
    changesMade = False
    
    selfCollide = particleShapeName + ".selfCollide"
    if(enableSelfCollide and not pm.getAttr(selfCollide)):
        pm.setAttr(selfCollide, True)
        changesMade = True
        util.LogInfo("Enabled %s selfCollide." % particleShapeName)
    
    friction = particleShapeName + ".friction"
    if(disableFriction and pm.getAttr(friction) > 0):
        pm.setAttr(friction, 0.0)
        changesMade = True
        util.LogInfo("Set %s friction = 0." % particleShapeName)
        
    ignoreSolverGravity = particleShapeName + ".ignoreSolverGravity"
    if(disableIgnoreGravity and pm.getAttr(ignoreSolverGravity)):
        pm.setAttr(ignoreSolverGravity, False)
        changesMade = True
        util.LogInfo("Disabled %s ignoreSolverGravity." % particleShapeName)
        
    renderType = particleShapeName + ".particleRenderType"
    if(changeRenderType and pm.getAttr(renderType) != 4):
        pm.setAttr(renderType, 4)
        changesMade = True
        util.LogInfo("Changed %s render type to spheres." % particleShapeName)
        
    nucleus = pm.ls(la.mel.getActiveNucleusNode(False, True))[0]
    nucleusName = nucleus.name()
    if(enableGroundPlane and not nucleus.attr("usePlane").get()):
        nucleus.setAttr("usePlane", True)
        changesMade = True
        util.LogInfo("Enabled %s ground plane" % nucleusName)
    
    if(enableGroundPlane and disableFriction and nucleus.attr("planeFriction").get() > 0):
        nucleus.setAttr("planeFriction", 0.0)
        changesMade = True
        util.LogInfo("Set %s ground plane friction = 0" % nucleusName)
    
    if(changeSpaceScale and abs(GetNucleusSpaceScale() - 0.01) > 0.001):
        nucleus.setAttr('spaceScale', 0.01)
        changesMade = True
        util.LogInfo("Set %s spaceScale to 0.01" % nucleusName)
    
    if(translateAbovePlane):
        positions = ParticlePositionsListForParticleShape(particleShapeName)
        if(positions):
            yMin = float('inf')
            for _, y, _ in zip(positions[0::3], positions[1::3], positions[2::3]):
                if(y < yMin) : yMin = y
            
            particleRadius = pm.getAttr(particleShapeName + ".radius")
            collideWidthScale = pm.getAttr(particleShapeName + ".collideWidthScale")
            yMin -= (particleRadius * collideWidthScale) + 0.001
            
            groundOriginY = nucleus.attr('planeOriginY').get()
            if(yMin < groundOriginY):
                diff = groundOriginY - yMin
                particleShapeObject = PymelObjectFromObjectName(particleShapeName)
                particleTransform = particleShapeObject.parentAtIndex(0)
                particleTransform.translateBy((0, diff, 0), space='world')
                changesMade = True
                util.LogInfo("Translated %s by %.3f in y to clear %s ground plane." 
                             % (particleShapeName, diff, nucleusName))

    # re-setting time slider in this way refreshes solver display etc.
    pm.currentTime(util.GetCurrentFrameNumber(), update=True)
    util.LogInfo("%sQuick scene setup complete." % ("" if(changesMade) else "No changes to make. "))


# END OF MODULE
###################################################
