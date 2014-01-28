import boidVectors.vector3 as bv3

import pymel.core as pm
import pymel.core.nodetypes as pmn  # Eclipse doesn't like pm.nodetypes for some reason... (perhaps an issue with the Pymel predefinitions?)
import logging
import os



######################################
def PackageName():
    return "PySwarm"

######################################
__utilLogger__ = logging.getLogger(PackageName())

def LogDebug(message, prefix=None):
    __utilLogger__.debug(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
def LogInfo(message, prefix=None):
    __utilLogger__.info(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
def LogWarning(message, prefix=None):
    __utilLogger__.warning(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
def LogError(message, prefix=None):
    __utilLogger__.error(("%s %s" % (prefix, message)) if(prefix is not None) else message)
    
def SetLoggingLevelDebug():
    __utilLogger__.setLevel(logging.DEBUG)
    LogDebug("Logging level set - DEBUG")

def SetLoggingLevelInfo():
    LogDebug("Logging level set - INFO")
    __utilLogger__.setLevel(logging.INFO)

######################################
def GetProjectRootDirectory():
    return pm.workspace.getPath()

def GetProjectWorkingDirectory():
    return pm.workspace.getcwd()

def GetCurrentSceneName():
    sceneFile = pm.system.sceneName()
    sceneFile = os.path.split(sceneFile)[1]
    
    return os.path.splitext(sceneFile)[0]
    
######################################
__SaveSceneScriptJobNumber__ = -1

#####
def AddSceneSavedScriptJobIfNecessary(saveMethod):
    global __SaveSceneScriptJobNumber__
    
    ClearSceneSavedScriptJobReference()
    
    methodName = saveMethod.__name__
    scriptJobsList = pm.scriptJob(listJobs=True)
    for scriptJobString in scriptJobsList:
        if(methodName in scriptJobsList):
            __SaveSceneScriptJobNumber__ = int(scriptJobString.split(':')[0])
            LogDebug("Found existing \"SceneSaved\" script job (#%d)" % __SaveSceneScriptJobNumber__)
            break
    
    if(__SaveSceneScriptJobNumber__ == -1):
        __SaveSceneScriptJobNumber__ = pm.scriptJob(event=("SceneSaved", saveMethod), killWithScene=True)
        LogInfo("Registered \"SceneSaved\" script job (job #%d)" % __SaveSceneScriptJobNumber__)

#####        
def RemoveSceneSavedScriptJob():
    global __SaveSceneScriptJobNumber__
    
    if(__SaveSceneScriptJobNumber__ != -1):
        if(pm.scriptJob(exists=__SaveSceneScriptJobNumber__)):
            pm.scriptJob(kill=__SaveSceneScriptJobNumber__)
            LogInfo("Removed \"SceneSaved\" script job #%d" % __SaveSceneScriptJobNumber__)
            ClearSceneSavedScriptJobReference()
        else:
            badRef =__SaveSceneScriptJobNumber__
            ClearSceneSavedScriptJobReference()
            raise RuntimeError("Cannot remove \"SavedScene\" script job #%d - reference number no longer valid!" % badRef)
    else:
        LogWarning("No \"SceneSaved\" script job currently registered.")

#####        
def ClearSceneSavedScriptJobReference():
    global __SaveSceneScriptJobNumber__
    __SaveSceneScriptJobNumber__ = -1

######################################            
def _ScriptNodeExists(scriptNodeName, isBefore):
    kwargs = { "query" : True }
    if(isBefore):
        kwargs["beforeScript"] = True
    else:
        kwargs["afterScript"] = True
    
    try:
        scriptString = pm.scriptNode(scriptNodeName, **kwargs)
        if(scriptString):
            return True
        else:
            return False
    except:
        return False

#####
def AddScriptNodesIfNecessary(swarmControllerModuleName, sceneSetupMethod, frameUpdateMethod, sceneCloseMethod):
    moduleHandle = ("__%s_IMPORT_FOR_SCRIPTNODE_UPDATES__" % PackageName().upper())
    scriptHeaderString = ("\
##################################################\n\
# Auto-generated by %s, please do not edit!!#\n\
##################################################\n\n" % PackageName())
    
    if(not _ScriptNodeExists("pySwarmOnSceneOpen", True)):
        importString = ("if(\"%s\" not in globals()): globals()[\"%s\"] = \
__import__(\"%s\", globals(), locals(), [\"%s\"], -1)" % 
                        (moduleHandle, moduleHandle, swarmControllerModuleName, swarmControllerModuleName))
        sceneOpenNode = pm.scriptNode(name="pySwarmOnSceneOpen", 
                                      beforeScript=("%s%s\n%s.%s()" % 
                                                    (scriptHeaderString, 
                                                     importString,
                                                     moduleHandle, sceneSetupMethod.__name__)),  
                                      scriptType=2, sourceType='python')
        pm.evalDeferred(importString)
        
        LogDebug("Added scene-open script node \"%s\" to Maya scene." % sceneOpenNode)

    if(not _ScriptNodeExists("pySwarmOnFrameUpdate", True)):        
        frameUpdateNode = pm.scriptNode(name="pySwarmOnFrameUpdate", 
                                        beforeScript=("%s%s.%s()" % 
                                                      (scriptHeaderString,
                                                       moduleHandle, frameUpdateMethod.__name__)),  
                                        scriptType=7, sourceType='python')
        
        LogDebug("Added frame-update script node \"%s\" to Maya scene." % frameUpdateNode)
    
    if(not _ScriptNodeExists("pySwarmOnSceneClose", False)): 
        sceneCloseNode = pm.scriptNode(name="pySwarmOnSceneClose", 
                                      afterScript=("%s%s.%s()" % 
                                                   (scriptHeaderString, 
                                                    moduleHandle, sceneCloseMethod.__name__)),  
                                      scriptType=2, sourceType='python')
       
        LogDebug("Added scene-close script node \"%s\" to Maya scene." % sceneCloseNode)

######################################
__DeferredEvaluationsQueue__ = []
__ModuleHandle__ = ("__%s_IMPORT_FOR_DEFERRED_EVALUATION__" % PackageName().upper())
__DeferredEvaluationString__ = ("%s._MakeDeferredEvaluations()" % __ModuleHandle__)

#####
def EvalDeferred(boundMethod, *args, **kwargs):
    """This nasty little piece of hackery is necessary because the Pymel version of evalDeferred is not
    usable from a object-oriented environment - all you get is a string literal to be executed
    from within the main module. 
    As such, this is the only way to provided the same functionality for bound methods from within
    modules and classes (Method adds this module to main, then evaluates bound methods via _MakeDeferredEvaluations).
    """
    global __DeferredEvaluationsQueue__
    global __ModuleHandle__
    global __DeferredEvaluationString__
    
    if(not callable(boundMethod)):
        raise TypeError("Non-callable object \"%s\" passed to EvalDeferred." % boundMethod)
    else:
        if(not __DeferredEvaluationsQueue__):
            importString = ("if(\"%s\" not in globals()): globals()[\"%s\"] = \
__import__(\"%s\", globals(), locals(), [\"%s\"], -1)" % 
                            (__ModuleHandle__, __ModuleHandle__, __name__, __name__))
            pm.evalDeferred(importString)
            pm.evalDeferred(__DeferredEvaluationString__)
        
        __DeferredEvaluationsQueue__.append((boundMethod, args, kwargs))
    
######
def _MakeDeferredEvaluations():    
    global __DeferredEvaluationsQueue__
    
    for commandTuple in __DeferredEvaluationsQueue__:
        command = commandTuple[0]
        arguments = commandTuple[1]
        keywords = commandTuple[2]
        
        command(*arguments, **keywords)
    
    del __DeferredEvaluationsQueue__[:]
    
######################################



######################################  
def InitVal(value, defaultValue):
    return value if value is not None else defaultValue

######################################
    
    

######################################
def PymelObjectFromObjectName(objectName, bypassTransformNodes=True):
    """Converts Maya object string to a Pymel object, if necessary.
    If the object is already a Pymel object, no action is taken.
    """
    if(isinstance(objectName, pm.PyNode)):
        return _GetPymelObjectWithType(objectName, None) if(bypassTransformNodes) else objectName 
    else:
        value = pm.PyNode(objectName)
        return _GetPymelObjectWithType(value, None) if(bypassTransformNodes) else value 
    
######################################
def GetSelectedParticleShapeNode(particleShapeName=None):
    selectionList = pm.ls(selection=True)
    for selectedObject in selectionList:
        result = _GetPymelObjectWithType(selectedObject, GetParticleType())
        if(result is not None and 
           (particleShapeName is None or result.name() == particleShapeName)):
            return result

    return None

######################################
def GetSelectedParticles(particleShapeName):
    selectedParticleShape = GetSelectedParticleShapeNode(particleShapeName)
    if(selectedParticleShape is not None):
        return ParticleIdsListForParticleShape(particleShapeName)
    else:
        selectionList = pm.ls(selection=True)
        returnList = []
        for selectedObject in selectionList:
            if(isinstance(selectedObject, pm.general.ParticleComponent)):
                candidateName = selectedObject.name().split(".pt[")[0]
                if(candidateName == particleShapeName):
                    for index in selectedObject.indicesIter():
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
    selectionList = pm.ls(selection=True)
    returnList = []
    
    for selectedObject in selectionList:
        result = _GetPymelObjectWithType(selectedObject, GetLocatorType())
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
    nucleus = pm.ls(pm.mel.getActiveNucleusNode(False, True))[0]
    return nucleus.attr('spaceScale').get()

######################################
def GetLocatorType():
    return pmn.Locator

def GetParticleType():
    return pmn.NParticle

def GetCurveType():
    return pmn.NurbsCurve

######################################
def ScriptJobsAreInScene():
    return False

# def AddSwarmScriptJobsToScene():
#     if(not ScriptJobsAreInScene()):
#         




######################################
def Vector3FromLocator(locator):
    if(isinstance(locator, pmn.Locator)):
        coOrdsString = locator.getPosition()
        coOrds = coOrdsString.split()
        return bv3.Vector3(float(coOrds[0]), float(coOrds[1]), float(coOrds[2]))     
    elif(isinstance(locator, str)):
        return Vector3FromLocator(PymelObjectFromObjectName(locator))
    else:
        return None
    
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

def Vector3FromPymelPoint(point):
    return bv3.Vector3(point.x, point.y, point.z)

######################################
def Vector3FromPymelVector(pymelVector):
    return bv3.Vector3(pymelVector.x, pymelVector.y, pymelVector.z)

def PymelVectorFromVector3(vector3):
    return pm.datatypes.Vector(vector3.x, vector3.y, vector3.z)

######################################
def ParticleIdsListForParticleShape(particleShapeName):
    return map(int, pm.getParticleAttr(particleShapeName + ".pt[:]", at='particleId', a=True))

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

######################################        
def AddStickinessPerParticleAttributeIfNecessary(particleShapeName):
    if(not pm.attributeQuery('stickinessScalePP', node=particleShapeName, exists=True)):
        pm.AddAttribute(particleShapeName, longName='stickinessScalePP', dataType='doubleArray')
        LogDebug("Added PP attribute stickinessScalePP to %s" % particleShapeName)
    if(not pm.attributeQuery('stickinessScalePP0', node=particleShapeName, exists=True)):
        pm.AddAttribute(particleShapeName, longName='stickinessScalePP0', dataType='doubleArray')
        LogDebug("Added PP attribute stickinessScalePP0 to %s" % particleShapeName)
        

# END OF MODULE
###################################################
