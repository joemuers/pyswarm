import boidBaseObject as bbo
import boidAgents.agentsController as bac
import boidAttributes.attributesController as bat
import boidBehaviours.behavioursController as bbc
import uiController as uic
import boidTools.util as util
import boidTools.agentSelectionWindow as asw
import boidTools.sceneInterface as scene
import boidResources.fileLocations as fl

import os
import sys
try:
    import cPickle as pickle
except:
    import pickle



###########################################
_SwarmInstances_ = []

#####
def InitialiseSwarm(particleShapeNode=None, sceneBounds1=None, sceneBounds2=None):
    return util.SafeEvaluate(True, _InitialiseSwarm, particleShapeNode, sceneBounds1, sceneBounds2)

#####
def _InitialiseSwarm(particleShapeNode=None, sceneBounds1=None, sceneBounds2=None):
    """Creates a new swarm instance for the given particle node.
    If a swarm already exists for that particle node, it will be replaced.
    """
    global _SwarmInstances_
    _SceneSetup(False)
    
    if(particleShapeNode is None):
        selectedParticleNodes = scene.GetSelectedParticleShapeNodes()
        if(selectedParticleNodes):
            newSwarms = [_InitialiseSwarm(particleNode, sceneBounds1, sceneBounds2) 
                         for particleNode in selectedParticleNodes]            
            return newSwarms if(len(newSwarms) > 1) else newSwarms[0]
        else:
            raise RuntimeError("No particle node specified - you must either select one in the scene \
or pass in a reference via the \"particleShapeNode\" argument to this method.")
    else:
        try:
            RemoveSwarmInstanceForParticle(particleShapeNode)
        except:
            pass
        
        newSwarm = SwarmController(particleShapeNode, sceneBounds1, sceneBounds2)
        _SwarmInstances_.append(newSwarm)
        newSwarm.showUI()
        
        util.LogInfo("Created new %s instance for nParticle %s" % (util.PackageName(), newSwarm.particleShapeName))
        
        return newSwarm

#####
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
        
    return None

##############################
def RemoveSwarmInstanceForParticle(particleShapeNode):
    RemoveSwarmInstance(GetSwarmInstanceForParticle(particleShapeNode))

#####
def RemoveSwarmInstance(swarmInstance):
    global _SwarmInstances_
    
    if(swarmInstance in _SwarmInstances_):
        swarmInstance.hideUI()
        _SwarmInstances_.remove(swarmInstance)
        
        util.LogInfo("%s instance for %s deleted." % (util.PackageName(), swarmInstance.particleShapeName))
    elif(swarmInstance is not None and isinstance(swarmInstance, SwarmController)):
        swarmInstance.hideUI()
        util.LogWarning("Attempt to delete unregistered swarm instance - likely causes:\n\
swarmController module as been reloaded, leaving \'orphan\' instances, or,\n\
an instance has been created indepedently by the user.\n\
It is recommended that swarm management is done only via the module methods provided.")
    elif(str(type(swarmInstance) == str(SwarmController))):
        raise RuntimeError("%s module-level variables missing - likely due to reload. Recommend you re-initialise completely." 
                           % util.PackageName())
    else:
        raise TypeError("Got %s of type %s (expected %s)." % (swarmInstance, type(swarmInstance), SwarmController))

#####
def RemoveAllSwarmInstances():
    for swarmInstance in _SwarmInstances_[:]:
        RemoveSwarmInstance(swarmInstance)

#############################         
_PICKLE_PROTOCOL_VERSION_ = 2 # Safer to stick to constant version rather than using "highest"

#####
def SaveSceneToFile(fileLocation=None):
    global _PICKLE_PROTOCOL_VERSION_
    global _SwarmInstances_
    
    fileLocation = util.InitVal(fileLocation, fl.SaveFileLocation())
    saveFile = open(fileLocation, "wb")
    pickle.dump(_SwarmInstances_, saveFile, _PICKLE_PROTOCOL_VERSION_)
    saveFile.close()
    
    util.LogInfo("Saved %s scene to file %s" % (util.PackageName(), fileLocation))
    
#####
def LoadSceneFromFile(fileLocation=None):
    global _SwarmInstances_
    
    fileLocation = util.InitVal(fileLocation, fl.SaveFileLocation())
    if(os.path.exists(fileLocation)):
        try:
            readFile = open(fileLocation, "rb")
            newInstances = pickle.load(readFile)
        except Exception as e:
            util.LogWarning("Cannot restore %s session - error \"%s\" while reading file: %s" % 
                            (util.PackageName(), e, fileLocation))
            raise e
        
        while(_SwarmInstances_):
            _SwarmInstances_.pop().hideUI()
        
        for swarmInstance in newInstances:
            swarmInstance.showUI()
            _SwarmInstances_.append(swarmInstance)
            
        util.LogInfo("Opened %s scene from file %s" % (util.PackageName(), fileLocation))
    else:
        raise ValueError("Cannot open file %s" % fileLocation)
    
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
            LoadSceneFromFile()
            util.LogInfo("Scene setup complete.")
        except:
            message = ("Scene setup complete.\n\tNo previous %s scene file found" % util.PackageName())
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
    
############################# 
if(__name__ == "__main__"):
    print "TODO - add unit tests"
else:
    util.LogInfo("%s initialised." % util.PackageName())
    _SceneSetup()

# END OF MODULE METHODS
#========================================================



#========================================================
class SwarmController(bbo.BoidBaseObject, uic.UiControllerDelegate):
    
    def __init__(self, particleShapeNode, sceneBounds1=None, sceneBounds2=None):
        if(not isinstance(particleShapeNode, scene.ParticlePymelType())):
            raise TypeError("Cannot create swarm with this node type (expected %s, got %s)." %
                            scene.ParticlePymelType(), type(particleShapeNode))
            
        if(sceneBounds1 is None and sceneBounds2 is None):
            locatorsList = scene.GetSelectedLocators()
            if(len(locatorsList) >= 2):
                sceneBounds1 = locatorsList[0]
                sceneBounds2 = locatorsList[1]
        
        self._attributesController = bat.AttributesController(particleShapeNode, sceneBounds1, sceneBounds2)
        self._behavioursController = bbc.BehavioursController(self._attributesController)
        self._agentsController = bac.AgentsController(self._attributesController, self._behavioursController)
        self._uiController = uic.UiController(self)
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
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._attributesController.globalAttributes)
                                                                            
        self.showUI()

#############################    
    def _getParticleShapeName(self):
        return self._attributesController.globalAttributes.particleShapeNode.name()
    particleShapeName = property(_getParticleShapeName)

#############################    
    def _getAttributesController(self):
        return self._attributesController
    attributesController = property(_getAttributesController)
    
#############################        
    def _onFrameUpdated(self):
        self._attributesController.onFrameUpdated()
        
        if(self._attributesController.globalAttributes.enabled):
            self._behavioursController.onFrameUpdated()
            self._agentsController.onFrameUpdated()
        
#############################    
    def enable(self):
        if(not self._attributesController.globalAttributes.enabled):
            self._attributesController.globalAttributes.enabled = True
            util.LogInfo("updates are now ACTIVE.", self.particleShapeName)
        else:
            util.LogWarning("updates already enabled.", self.particleShapeName)

########
    def disable(self):
        self._attributesController.globalAttributes.enabled = False
        util.LogInfo("updates DISABLED.", self.particleShapeName)
        
########
    def showUI(self):
        self._uiController.buildUi(("%s - %s" % (util.PackageName(), self.particleShapeName)), self._attributesController)

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
        
        particleIds = [agent.particleId for agent in currentSelection]
        scene.SelectParticlesInList(particleIds, self.particleShapeName) 
        
########
    def showAssignAgentsWindowForBehaviour(self, behaviourId):
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        currentSelection = [agent.particleId for agent in self._agentsController.getAgentsFollowingBehaviour(behaviour)]
        
        self._behaviourAssignmentSelectionWindow.dataBlob = behaviourId
        self._behaviourAssignmentSelectionWindow.show("Assign agents to \"%s\"" % behaviourId, 
                                                      currentSelection, self._onAgentSelectionCompleted)  

########
    def assignAgentsToBehaviour(self, agentIdsList, behaviourId):
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        self._agentsController.makeAgentsFollowBehaviour(agentIdsList, behaviour)
 
########    
    def getAssignedAgentIdsForBehaviour(self, behaviourId):
        behaviour = self._behavioursController.behaviourWithId(behaviourId)
        return [agent.particleId 
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
        deletedBehaviour = self._behavioursController.removeBehaviourForId(deletedBehaviourId)
        agentsFollowingOldBehaviour = self._agentsController.getAgentsFollowingBehaviour(deletedBehaviour)
        
        self._agentsController.makeAgentsFollowDefaultBehaviour(agentsFollowingOldBehaviour)
        self._uiController.removeBehaviourFromUI(deletedAttributes)
        
        util.LogInfo("Removed behaviour \"%s\"" % deletedBehaviourId)
        
##############################
    def _onAgentSelectionCompleted(self, selectionWindow, selectedAgentsList, selectionDisplayString):
        """Callback for agent selection window."""
        if(selectionWindow is self._behaviourAssignmentSelectionWindow):
            behaviourId = selectionWindow.dataBlob
            behaviour = self._behavioursController.behaviourWithId(behaviourId)
            defaultBehaviour = self._behavioursController.defaultBehaviour
            
            toUnassign = selectionWindow.originalSelection.difference(selectedAgentsList)
            if(toUnassign):
                if(behaviour is defaultBehaviour):
                    util.LogWarning("Cannot implicitly un-assign agents from default behaviour \"%s\"." % 
                                    behaviourId)
                else:
                    self._agentsController.makeAgentsFollowDefaultBehaviour(toUnassign)
            
            self._agentsController.makeAgentsFollowBehaviour(selectedAgentsList, behaviour)
            self._behaviourAssignmentSelectionWindow.dataBlob = None
            
            if(selectedAgentsList):
                util.LogInfo("The following agents are now assigned to behaviour \"%s\": %s." %
                             (behaviourId, ', '.join([str(agentId) for agentId in selectedAgentsList])))
            elif(behaviour is not defaultBehaviour):
                util.LogInfo("All agents previously following \"%s\" now assigned to default behaviour \"%s\"." 
                             % (behaviourId, defaultBehaviour.behaviourId))
                

# END OF CLASS - SwarmController
##################################