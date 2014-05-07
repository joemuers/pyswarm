import boidBaseObject as bbo
import boidAgents.agentsController as bac
import boidAttributes.attributesController as bat
import boidBehaviours.behavioursController as bbc
import uiController as uic
import boidTools.util as util
import boidTools.agentSelectionWindow as asw
import boidTools.sceneInterface as scene
import boidResources.fileLocations as fl
import boidResources.packageInfo as pi

import os
import sys
try:
    import cPickle as pickle
except:
    import pickle



###########################################
_SwarmInstances_ = []

#####
def _InitialiseSwarm(particleShapeNode=None, boundingLocators=None):
    """Creates a new swarm instance for the given particle node.
    If a swarm already exists for that particle node, it will be replaced.
    """
    global _SwarmInstances_
    _SceneSetup(False)  
    
    if(particleShapeNode is None):
        selectedParticleNodes = scene.GetSelectedParticleShapeNodes()
        if(selectedParticleNodes):
            newSwarms = [_InitialiseSwarm(particleNode, boundingLocators) 
                         for particleNode in selectedParticleNodes]            
            return newSwarms if(len(newSwarms) > 1) else newSwarms[0]
        else:
            raise RuntimeError("No particle node specified - you must either select one in the scene " +
                               "or pass in a reference via the \"particleShapeNode\" argument to this method.")
    else:
        try:
            RemoveSwarmInstanceForParticle(particleShapeNode)
        except:
            pass
        
        if(isinstance(particleShapeNode, basestring)):
            particleShapeNode = scene.PymelObjectFromObjectName(particleShapeNode, True, scene.ParticlePymelType())
        elif(not isinstance(particleShapeNode, scene.ParticlePymelType())):
            raise TypeError("particleShapeNode unrecognised (expected Maya object path to nParticle instance, " +
                            (" or Pymel type %s, got %s)." % (scene.ParticlePymelType(), type(particleShapeNode))))
        
        if(boundingLocators is None):
            selectedLocators = scene.GetSelectedLocators()
            boundingLocators = selectedLocators if(len(selectedLocators) >= 2) else None
        else:
            if(not isinstance(boundingLocators, (tuple, list)) or len(boundingLocators) < 2):
                raise ValueError("boundingLocators unrecognised (expected (Locator,Locator) tuple, or <None> - got: %s)." 
                                 % boundingLocators)
            elif(isinstance(boundingLocators[0], basestring) and isinstance(boundingLocators[1], basestring)):
                locator1 = scene.PymelObjectFromObjectName(boundingLocators[0], True, scene.LocatorPymelType())
                locator2 = scene.PymelObjectFromObjectName(boundingLocators[1], True, scene.LocatorPymelType())
                boundingLocators = (locator1, locator2)
            elif(not isinstance(boundingLocators[0], scene.LocatorPymelType()) or 
                 not isinstance(boundingLocators[1], scene.LocatorPymelType())):
                raise TypeError("boundingLocators unrecognised (expected tuple pair of Maya object paths to Locator instances, " +
                                ("tuple pair of Pymel type %s, or <None> - got (%s,%s))." 
                                 % (scene.LocatorPymelType(), type(boundingLocators[0]), type(boundingLocators[1]))))
            
        
        newSwarm = SwarmController(particleShapeNode, boundingLocators)
        _SwarmInstances_.append(newSwarm)
        newSwarm.showUI()
        
        util.LogInfo("Created new %s instance for nParticle %s" % (pi.PackageName(), newSwarm.particleShapeName))
        
        return newSwarm

#####
def InitialiseSwarm(particleShapeNode=None, boundingLocators=None):
    return util.SafeEvaluate(True, _InitialiseSwarm, particleShapeNode, boundingLocators)
InitialiseSwarm.__doc__ = _InitialiseSwarm.__doc__ 

#############################
def Show():
    """Will make the UIs visible (if not already) for all existing swarm instances."""
    global _SwarmInstances_
    for swarmInstance in _SwarmInstances_:
        swarmInstance.showUI()

#############################
def GetSwarmInstanceForParticle(particleShapeNode):
    """Gets the corresponding swarm instance for the given particle node,
    if it exists (otherwise returns None).
    """
    global _SwarmInstances_
    pymelShapeNode = scene.PymelObjectFromObjectName(particleShapeNode, True)
    for swarmController in _SwarmInstances_:
        if(pymelShapeNode.name() == swarmController.particleShapeName):
            return swarmController
        
    util.LogError("No %s instance exists for %s" (pi.PackageName(), particleShapeNode))

##############################
def RemoveSwarmInstanceForParticle(particleShapeNode):
    RemoveSwarmInstance(GetSwarmInstanceForParticle(particleShapeNode))

#####
def _RemoveSwarmInstance(swarmInstance):
    global _SwarmInstances_
    
    if(swarmInstance in _SwarmInstances_):
        swarmInstance.hideUI()
        _SwarmInstances_.remove(swarmInstance)
        name = swarmInstance.particleShapeName
        swarmInstance._decommision()
        
        util.LogInfo("%s instance for %s deleted." % (pi.PackageName(), name))
    elif(swarmInstance is not None and isinstance(swarmInstance, SwarmController)):
        swarmInstance.hideUI()
        swarmInstance._decommision()
        
        util.LogWarning("Attempt to delete unregistered swarm instance - likely causes:\n\
swarmController module as been reloaded, leaving \'orphan\' instances, or,\n\
an instance has been created indepedently by the user.\n\
It is recommended that swarm management is done only via the module methods provided.")
    elif(str(type(swarmInstance) == str(SwarmController))):
        raise RuntimeError("%s module-level variables missing - likely due to reload. Recommend you re-initialise completely." 
                           % pi.PackageName())
    else:
        raise TypeError("Got %s of type %s (expected %s)." % (swarmInstance, type(swarmInstance), SwarmController))

#####
def RemoveSwarmInstance(swarmInstance):
    return util.SafeEvaluate(True, _RemoveSwarmInstance, swarmInstance)
RemoveSwarmInstance.__doc__ = _RemoveSwarmInstance.__doc__

#####
def RemoveAllSwarmInstances():
    for swarmInstance in _SwarmInstances_[:]:
        RemoveSwarmInstance(swarmInstance)

#############################         
_PICKLE_PROTOCOL_VERSION_ = 2 # Safer to stick to constant version rather than using "highest"

#####
def _SaveSceneToFile(fileLocation=None):
    global _PICKLE_PROTOCOL_VERSION_
    global _SwarmInstances_
    
    fileLocation = util.InitVal(fileLocation, fl.SaveFileLocation())
    saveFile = open(fileLocation, "wb")
    try:
        pickle.dump(_SwarmInstances_, saveFile, _PICKLE_PROTOCOL_VERSION_)
        saveFile.close()
        util.LogInfo("Saved %s scene to file %s" % (pi.PackageName(), fileLocation))
    except Exception, e:
        saveFile.close()
        os.remove(saveFile.name)
        util.LogError("Could not save PySwarm scene - Pickling error: %s" % e)
    
#####
def SaveSceneToFile(fileLocation=None):
    return util.SafeEvaluate(True, _SaveSceneToFile, fileLocation)
SaveSceneToFile.__doc__ = _SaveSceneToFile.__doc__
    
#####
def _LoadSceneFromFile(fileLocation=None):
    global _SwarmInstances_
    
    fileLocation = util.InitVal(fileLocation, fl.SaveFileLocation())
    if(os.path.exists(fileLocation)):
        try:
            readFile = open(fileLocation, "rb")
            
            while(_SwarmInstances_): # it's VERY IMPORTANT to tear down the UI components *first* before rebuilding new ones because,
                _SwarmInstances_.pop().hideUI() # in another little Pymel quirk, they are referenced by "handle" and not pointer address
                                                # which means that the wires get crossed if we create the new before deleting the old
            newInstances = pickle.load(readFile)
        except Exception as e:
            util.LogWarning("Cannot restore %s session - error \"%s\" while reading file: %s" % 
                            (pi.PackageName(), e, fileLocation))
            raise e
        
        
        for swarmInstance in newInstances:
            swarmInstance.showUI()
            _SwarmInstances_.append(swarmInstance)
            
        util.LogInfo("Opened %s scene from file %s" % (pi.PackageName(), fileLocation))
    else:
        raise ValueError("Cannot open file %s" % fileLocation)

#####
def LoadSceneFromFile(fileLocation=None):
    return util.SafeEvaluate(True, _LoadSceneFromFile, fileLocation)
LoadSceneFromFile.__doc__ = _LoadSceneFromFile.__doc__

#############################        
def _OnFrameUpdated():
    global _SwarmInstances_
    for swarmInstance in _SwarmInstances_:
        swarmInstance._onFrameUpdated()

###########################################
_HaveRunSceneSetup = False

#####
def _SceneSetup(calledExternally=True):
    global _HaveRunSceneSetup
    
    if(not _HaveRunSceneSetup):
        moduleSelf = sys.modules[__name__]
        util.AddScriptNodesIfNecessary(moduleSelf, _SceneSetup, _OnFrameUpdated, _SceneTeardown)
        util.AddSceneSavedScriptJobIfNecessary(SaveSceneToFile)
        
        try:
            _LoadSceneFromFile()
            util.LogInfo("Scene setup complete.")
        except:
            message = ("Scene setup complete.\n\t\t\tNo previous %s scene file found" % pi.PackageName())
            if(not calledExternally):
                message += '.'
            else:
                message += (" - run %s method %s to create a swarm instance." % (__name__, InitialiseSwarm.__name__))
            util.LogInfo(message)
            
        _HaveRunSceneSetup = True

#####
def _SceneTeardown():
    global _HaveRunSceneSetup
    
    util.ClearSceneSavedScriptJobReference()
    for swarmInstance in _SwarmInstances_:
        swarmInstance.hideUI()
    
    util.LogInfo("Cleaned up resources.")
    _HaveRunSceneSetup = False

# END OF MODULE METHODS
#========================================================



#========================================================
class SwarmController(bbo.BoidBaseObject, uic.UiControllerDelegate):
    
    def __init__(self, particleShapeNode, boundingLocators=None):
        super(SwarmController, self).__init__()
        
        self._attributesController = bat.AttributesController(particleShapeNode, SaveSceneToFile, boundingLocators)
        self._behavioursController = bbc.BehavioursController(self._attributesController)
        self._agentsController = bac.AgentsController(self._attributesController, self._behavioursController)
        self._uiController = uic.UiController(self._attributesController, self)
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._attributesController.globalAttributes)
        
        self._agentsController._buildParticleList()

#############################        
    def __str__(self):
        return self._agentsController.__str__()

########    
    def _getMetaStr(self):
        return self._agentsController.metaStr

#############################    
    def __getstate__(self):
        state = super(SwarmController, self).__getstate__()
        state["_behaviourAssignmentSelectionWindow"] = None
        
        return state

########        
    def __setstate__(self, state):
        super(SwarmController, self).__setstate__(state)
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._globalAttributes)
                                                                            
        self.showUI()

#############################
    def _getGlobalAttributes(self):
        return self._attributesController.globalAttributes
    _globalAttributes = property(_getGlobalAttributes)
    
#############################    
    def _getParticleShapeName(self):
        return self._globalAttributes.particleShapeNode.name()
    particleShapeName = property(_getParticleShapeName)

#############################    
    def _getAttributesController(self):
        return self._attributesController
    attributesController = property(_getAttributesController)
    
#############################        
    def _onFrameUpdated(self):
        try:
            self._globalAttributes.setStatusReadoutWorking(1, "Reading...")
            
            self._attributesController.onFrameUpdated()
            
            if(self._globalAttributes.enabled):
                self._behavioursController.onFrameUpdated()
                self._agentsController.onFrameUpdated()
            
            self._globalAttributes.setStatusReadoutIdle()
            
            self._attributesController.onCalculationsCompleted()
            self._behavioursController.onCalculationsCompleted()
            self._agentsController.onCalculationsCompleted()
            
        except Exception as e:
            self._globalAttributes.setStatusReadoutError()
            util.StopPlayback()
            util.LogException(e)

#############################    
    def enable(self):
        if(not self._globalAttributes.enabled):
            self._globalAttributes.enabled = True
            util.LogInfo("updates are now ACTIVE.", self.particleShapeName)
        else:
            util.LogWarning("updates already enabled.", self.particleShapeName)

########
    def disable(self):
        self._globalAttributes.enabled = False
        util.LogInfo("updates DISABLED.", self.particleShapeName)
        
########
    def _decommision(self):
        self._attributesController = None
        self._behavioursController = None
        self._agentsController = None
        self._uiController = None
        self._behaviourAssignmentSelectionWindow  = None
        
########
    def showUI(self):
        self._uiController.buildUi()

########            
    def hideUI(self):
        self._uiController.hideUI()
        self._behaviourAssignmentSelectionWindow.closeWindow()
 
########       
    def openFile(self, filePath):
        util.EvalDeferred(LoadSceneFromFile, filePath)

######## 
    def saveToFile(self, filePath=None):
        SaveSceneToFile(filePath)
        
########
    def showDebugLogging(self, show):
        if(show):
            util.SetLoggingLevelDebug()
        else:
            util.SetLoggingLevelInfo()
        
########
    def showPreferencesWindow(self):
        self._attributesController.showPreferencesWindow()
 
########
    def quitSwarmInstance(self):
        util.EvalDeferred(RemoveSwarmInstance, self)
        
########
    def refreshInternals(self):
        self._attributesController.onFrameUpdated()
        self._behavioursController.onFrameUpdated()
        self._agentsController.refreshInternals()
        
        self._attributesController.purgeRepositories()
        
        util.LogInfo("Refreshed internal state...")

########        
    def restoreDefaultValues(self, behaviourId=None):
        self._attributesController.restoreDefaultAttributeValuesFromFile(behaviourId)
        
########
    def makeValuesDefault(self, behaviourId=None):
        util.LogDebug("Re-setting default attribute values with current values...")
        self._attributesController.makeCurrentAttributeValuesDefault(behaviourId)
        
########
    def changeDefaultBehaviour(self, behaviourId):
        oldDefaultBehaviourId = self._globalAttributes.defaultBehaviourId
        if(self._attributesController.changeDefaultBehaviour(behaviourId)):
            self._uiController.updateDefaultBehaviourInUI(oldDefaultBehaviourId, self._globalAttributes.defaultBehaviourId)
        
########       
    def addNewBehaviour(self, behaviourTypeName):
        newBehaviour = self._attributesController.addBehaviourForTypeName(behaviourTypeName)
        if(newBehaviour is not None):
            self._onNewBehaviourAttributesAdded(newBehaviour)
            
########
    def removeBehaviour(self, behaviourId):
        deletedAttributes = self._attributesController.removeBehaviour(behaviourId)
        if(deletedAttributes is not None):
            self._onBehaviourAttributesDeleted(deletedAttributes)
        else:
            util.LogWarning("Could not remove behaviour \"%s\"" % behaviourId)

########           
    def removeAllBehaviours(self):
        for behaviourId in self._attributesController.behaviourTypeNamesList():
            self.removeBehaviour(behaviourId)

########          
    def makeAgentsWithBehaviourSelected(self, behaviourId, invertSelection):
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        currentSelection = self._agentsController.getAgentsFollowingBehaviour(behaviour)
        if(invertSelection):
            allAgents = set(self._agentsController.allAgents)
            currentSelection = list(allAgents.difference(set(currentSelection)))
        
        particleIds = [agent.agentId for agent in currentSelection]
        scene.SelectParticlesInList(particleIds, self.particleShapeName) 
        
########
    def showAssignAgentsWindowForBehaviour(self, behaviourId):
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        currentSelection = [agent.agentId for agent in self._agentsController.getAgentsFollowingBehaviour(behaviour)]
        
        self._behaviourAssignmentSelectionWindow.dataBlob = behaviourId
        self._behaviourAssignmentSelectionWindow.show("Assign agents to \"%s\"" % behaviourId, 
                                                      currentSelection, self._onAgentSelectionCompleted)  
        
########
    def quickSceneSetup(self):
        scene.QuickSceneSetup(self.particleShapeName, 
                              self._globalAttributes.quickSetupEnableSelfCollide, self._globalAttributes.quickSetupDisableFriction,
                              self._globalAttributes.quickSetupDisableIgnoreGravity, self._globalAttributes.quickSetupChangeRenderType,
                              self._globalAttributes.quickSetupEnableGroundPlane, self._globalAttributes.quickSetupChangeSpaceScale,
                              self._globalAttributes.quickSetupTranslateAbovePlane)

########
    def assignAgentsToBehaviour(self, agentIdsList, behaviourId):
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        self._agentsController.makeAgentsFollowBehaviour(agentIdsList, behaviour)
 
########    
    def getAssignedAgentIdsForBehaviour(self, behaviourId):
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        return [agent.agentId 
                for agent in sorted(self._agentsController.getAgentsFollowingBehaviour(behaviour))]
            
#############################                  
    def addClassicBoidBehaviour(self):
        newBehaviour = self._attributesController.addClassicBoidAttributes()
        self._onNewBehaviourAttributesAdded(newBehaviour)
        
########
    def addGoalDrivenBehaviour(self, wallLipGoal=None, basePyramidGoalHeight=None, finalGoal=None):
        newBehaviour = self._attributesController.addGoalDrivenAttributes(wallLipGoal, basePyramidGoalHeight, finalGoal)
        self._onNewBehaviourAttributesAdded(newBehaviour)
        
########        
    def addFollowPathBehaviour(self, pathCurve=None):
        newBehaviour = self._attributesController.addFollowPathAttributes(pathCurve)
        self._onNewBehaviourAttributesAdded(newBehaviour)

#############################      
    def _onNewBehaviourAttributesAdded(self, newBehaviourAttributes):
        self._behavioursController.createBehaviourForNewAttributes(newBehaviourAttributes)
        self._uiController.addNewBehaviourToUI(newBehaviourAttributes)
        
        util.LogInfo("Added new behaviour \"%s\"" % newBehaviourAttributes.behaviourId)

#############################        
    def _onBehaviourAttributesDeleted(self, deletedAttributes):
        deletedBehaviourId = deletedAttributes.behaviourId
        deletedBehaviour = self._behavioursController.removeBehaviourWithId(deletedBehaviourId)
        agentsFollowingOldBehaviour = self._agentsController.getAgentsFollowingBehaviour(deletedBehaviour)
        
        self._agentsController.makeAgentsFollowDefaultBehaviour(agentsFollowingOldBehaviour)
        self._uiController.removeBehaviourFromUI(deletedAttributes)
        
        util.LogInfo("Removed behaviour \"%s\"" % deletedBehaviourId)
        
##############################
    def _onAgentSelectionCompleted(self, selectionWindow, selectedAgentsList, selectionDisplayString):
        """Callback for agent selection window."""
        if(selectionWindow is self._behaviourAssignmentSelectionWindow):
            behaviourId = selectionWindow.dataBlob
            defaultBehaviourId = self._globalAttributes.defaultBehaviourId
            
            toUnassign = selectionWindow.originalSelection.difference(selectedAgentsList)
            if(toUnassign):
                if(behaviourId == defaultBehaviourId):
                    util.LogWarning("Cannot implicitly un-assign agents from default behaviour \"%s\"." % 
                                    behaviourId)
                else:
                    self._agentsController.makeAgentsFollowDefaultBehaviour(toUnassign)

            behaviour = self._behavioursController.behaviourWithId(behaviourId)            
            self._agentsController.makeAgentsFollowBehaviour(selectedAgentsList, behaviour)
            self._behaviourAssignmentSelectionWindow.dataBlob = None
            
            if(selectedAgentsList):
                util.LogInfo("The following agents are now assigned to behaviour \"%s\": %s." %
                             (behaviourId, ', '.join([str(agentId) for agentId in selectedAgentsList])))
            elif(behaviourId != defaultBehaviourId):
                util.LogInfo("All agents previously following \"%s\" now assigned to default behaviour \"%s\"." 
                             % (behaviourId, defaultBehaviourId))
                

# END OF CLASS - SwarmController
##################################




#############################
# RUN ON IMPORT METHODS
 
if(__name__ == "__main__"):
    print "TODO - add unit tests"
else:
    util.LogInfo("%s initialised." % pi.PackageName())
    _SceneSetup() # Note this must be run *after* everything else in this module has been defined.
