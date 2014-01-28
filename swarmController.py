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
try:
    import cPickle as pickle
except:
    import pickle



###########################################
_SwarmInstances_ = []

#####
def InitialiseSwarm(particleShapeNode=None, sceneBounds1=None, sceneBounds2=None):
    """Creates a new swarm instance for the given particle node.
    If a swarm already exists for that particle node, it will be replaced.
    """
    global _SwarmInstances_
    _SceneSetup(False)
    
    if(particleShapeNode is None):
        particleShapeNode = scene.GetSelectedParticleShapeNode()
        if(particleShapeNode is None):
            raise RuntimeError("No particle node specified - you must either select one in the scene \
or pass in a reference via the \"particleShapeNode\" argument to this method.")
    
    try:
        RemoveSwarmInstanceForParticle(particleShapeNode)
    except:
        pass
    
    newSwarm = SwarmController(particleShapeNode, sceneBounds1, sceneBounds2)
    _SwarmInstances_.append(newSwarm)
    newSwarm.showUI()
    
    return newSwarm

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
        
        util.LogInfo("%s instance %s deleted." % (util.PackageName(), swarmInstance.particleShapeName))
    elif(swarmInstance is not None and isinstance(swarmInstance, SwarmController)):
        swarmInstance.hideUI()
        util.LogWarning("Attempt to delete unregistered swarm instance - likely causes:\n\
swarmController module as been reloaded, leaving \'orphan\' instances, or,\n\
an instance has been created indepedently by the user.\n\
It is recommended that swarm management is done only via the module methods provided.")
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
        util.AddScriptNodesIfNecessary(__name__, _SceneSetup, _OnFrameUpdated, _SceneTeardown)
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
        
        self._attributesController = bat.AttributesController(self._requestedLeaderSelectForBehaviour, 
                                                              sceneBounds1, sceneBounds2)
        self._agentsController = bac.AgentsController(self._attributesController, particleShapeNode)
        self._behavioursController = bbc.BehavioursController(self._attributesController, self._agentsController)
        self._uiController = uic.UiController(self)
        self._agentsController._buildParticleList()
        
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._agentsController)
        self._leaderAgentsSelectionWindow = asw.AgentSelectionWindow(self._agentsController)

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
        state["_leaderAgentsSelectionWindow"] = None
        
        return state

########        
    def __setstate__(self, state):
        super(SwarmController, self).__setstate__(state)
        
        self._behaviourAssignmentSelectionWindow = asw.AgentSelectionWindow(self._agentsController)
        self._leaderAgentsSelectionWindow = asw.AgentSelectionWindow(self._agentsController)
        
        self.showUI()

#############################    
    def _getParticleShapeName(self):
        return self._agentsController.particleShapeName
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
        self._leaderAgentsSelectionWindow.closeWindow()
 
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
        behaviourAttributes = self._attributesController.behaviourAttributesForId(behaviourId)
        behaviour = self._behavioursController.behaviourForAttributes(behaviourAttributes)
        currentSelection = self._agentsController.getAgentsFollowingBehaviour(behaviour)
        if(invertSelection):
            allAgents = set(self._agentsController.allAgents)
            currentSelection = list(allAgents.difference(set(currentSelection)))
        
        particleIds = map(lambda agent: agent.particleId, currentSelection)
        scene.SelectParticlesInList(particleIds, self.particleShapeName) 
        
########
    def showAssignAgentsWindowForBehaviour(self, behaviourId):
        behaviourAttributes = self._attributesController.behaviourAttributesForId(behaviourId)
        behaviour = self._behavioursController.behaviourForAttributes(behaviourAttributes)
        currentSelection = self._agentsController.getAgentsFollowingBehaviour(behaviour)
        
        self._behaviourAssignmentSelectionWindow.dataBlob = behaviourAttributes
        self._behaviourAssignmentSelectionWindow.show("Assign agents to \"%s\"" % behaviourAttributes.behaviourId, 
                                        currentSelection, self._onAgentSelectionCompleted)  

########
    def assignAgentsToBehaviour(self, agentIdsList, behaviourId):
        behaviourAttributes = self._attributesController.behaviourAttributesForId(behaviourId)
        behaviour = self._behavioursController.behaviourForAttributes(behaviourAttributes)
        self._agentsController.makeAgentsFollowBehaviour(agentIdsList, behaviour, behaviourAttributes)
 
########        
    def makeLeaderAgentsSelectedForBehaviour(self, behaviourId):
        self._requestedLeaderSelectForBehaviour(behaviourId, False)
        
########       
    def showLeaderSelectWindowForBehaviour(self, behaviourId):
        self._requestedLeaderSelectForBehaviour(behaviourId, True)
        
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
        deletedBehaviour = self._behavioursController.removeBehaviourForAttributes(deletedAttributes)
        agentsFollowingOldBehaviour = self._agentsController.getAgentsFollowingBehaviour(deletedBehaviour)
        defaultAttributes = self._attributesController.defaultBehaviourAttributes
        defaultBehaviour = self._behavioursController.defaultBehaviour
        
        self._agentsController.makeAgentsFollowBehaviour(agentsFollowingOldBehaviour, defaultBehaviour, defaultAttributes)
        self._uiController.removeBehaviourFromUI(deletedAttributes)
        
        util.LogInfo("Removed behaviour \"%s\"" % deletedAttributes.behaviourId)
        
#############################
    def _requestedLeaderSelectForBehaviour(self, behaviourAttributes, isChangeRequest):
        if(isinstance(behaviourAttributes, str)):
            behaviourAttributes = self._attributesController.behaviourAttributesForId(behaviourAttributes)
            
        behaviour = self._behavioursController.behaviourForAttributes(behaviourAttributes)
        currentSelection = behaviour.allLeaders()
        if(isChangeRequest):
            self._leaderAgentsSelectionWindow.dataBlob = behaviourAttributes
            self._leaderAgentsSelectionWindow.show("Select leader agents for \"%s\"" % behaviourAttributes.behaviourId,
                                               currentSelection, self._onAgentSelectionCompleted)
        else:
            particleIds = map(lambda agent: agent.particleId, currentSelection)
            scene.SelectParticlesInList(particleIds, self.particleShapeName)
        
##############################
    def _onAgentSelectionCompleted(self, selectionWindow, selectedAgentsList, selectionDisplayString):
        """Callback for agent selection window."""
        if(selectionWindow is self._behaviourAssignmentSelectionWindow):
            attributes = self._behaviourAssignmentSelectionWindow.dataBlob
            behaviour = self._behavioursController.behaviourForAttributes(attributes)
            
            self._agentsController.makeAgentsFollowBehaviour(selectedAgentsList, behaviour, attributes)
            self._behaviourAssignmentSelectionWindow.dataBlob = None
        elif(selectionWindow is self._leaderAgentsSelectionWindow):
            attributes = self._leaderAgentsSelectionWindow.dataBlob
            behaviour = self._behavioursController.behaviourForAttributes(attributes)
            
            for agent in selectedAgentsList:
                behaviour.makeLeader(agent)
            attributes.setLeadersAgentsTextDisplay(selectionDisplayString)
            self._leaderAgentsSelectionWindow.dataBlob = None
        

# END OF CLASS - SwarmController
##################################